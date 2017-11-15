Mega File - Web 500
===================

## Scenario ##
We've got a high profile client who needs to get a target's passcode. Something about rockets? IDK, they call him rocketman. Whatever, who cares? We're getting a big pay day if we can deliver. We're giving you a site that the target uses for file sharing, they seem like the next Equifax. Trusting that you can get this done.

Flag: **RC3-2017{5910752SHWP6177-soft_kitty}**

Hints given:
* The world is so much better when people are transparent.
* Don't you hate it when developers get sloppy with their swp files?
* word on the street is that the megafile devS love to SuRF

## Solution ##
So given the scenario, we know that our goal is to get one or more files from the "target's" account. There are a few vulnerabilities to take advantage of in order to get the target's files.

For a quick overview, one step of many is to discover https://megafile.fun/cgi-bin/get_xml.cgi, which gives you (1) local file inclusion (via path traversal and null byte injection) and allows you to get /var/www/megafile/config.ini which has the redis host, port and password (needed later). Another required step is (2) finding the development site, located at abqtt.supersecret.dev-test.megafile.fun, which can be found by viewing cert transparency logs for the megafile.fun domain. Once here you need to (3) get /.report-uri.php.swp and /.functions.php.swp so you can see the source code of these files, which reveals a "hidden" paremeter that can be specified called `url` to /report-uri.php. From here you can perform (4) SSRF (host/port injection) and you can eventually find an HTTP-based API running locally on port 8080. After learning how the service works, you can perform (5) SSRF (CRLF injection) against this to add a share relationship to the Redis instance on db.megafile.fun between nk-rocket-man and whatever account. This share gets replicatd from Redis to the shares table in the production database (which can be discovered from functions.php in the dev app), meaning that you can share files to and from any account via Redis and have this share pushed to the prod web app. So you add a share from nk-rocket-man (id of 2) to your prod account. Then you can use the regular interface to view his files. He has a file named "message.txt" and this has the flag in it. ez pz amirite?

Now for some more detail! So when you get to the web app you can figure out one possible way to get nk-rocket-man's files is to have him share his files with you somehow. It's a simple idea, but getting this share in place isn't so easy.

(1) As you use the application you'll find that when you upload an XML file on the settings page, there's a way to view your most recently uploaded XML file. When you click the link the app displays, it brings you to https://megafile.fun/cgi-bin/get_xml.cgi?name=<username>.xml. This is a perl script (yucky, I know) that gets the filename you gave. The script adds the full path of where xml uploads go to the variable and there is a regex to make sure this variable is in the right path. The regex is `|^/var/www/megafile/xml_uploads|`. This regex only checks that the path starts with the intended path which means you could perform path traversal to get any file on the system. But there's also a check on the file extension to make sure you can only retrieve XML files which is `/$user\.xml$/`. This isn't a terrible regex because it ensures that the name ends with the user's username followed by `.xml`. What defeats this regex is a null byte injection. Perl is fine with having null bytes in strings, so checking a variable like `poop\0user.xml` against the regex will pass. But when passing this same variable to Perl's open function, C libraries are used under the hood which terminate strings at a null byte. This means that the open function only receives `poop` instead of the entire string from Perl (a quick note: some version of Perl patched this and I was way too lazy to install an old version to get this to work, so I fudged it a bit. Try Perl 5.10 and that should work without my silly hack). So with this path traversal and null byte injection, we can bypass the path and filetype restrictions to retrieve any file on the system that the www-data user can read (AKA LFI)! The final payload to view the config.ini file would be:

```http
https://megafile.fun/cgi-bin/get_xml.cgi?name=../config.ini%00<username>.xml
```

Now you could try viewing all the source code for the application, which is always a good step in any web app assessment. If you get the functions.php file, you'll notice a config file being parsed that contains some creds. So using the payload shown previously you could get that file. The key piece of information given from this file is the redis host and password which will be used later.

(2) At this point, there isn't really much left to do on megafile.fun, the prod web app. So we need to find something else, which the landing page's blurb about a recent acquisition was supposed to hint at. Another slight hint is the usage of real domain names and TLS certs, which isn't super common in CTF challenges and they were chosen for a reason! Sure you could try brute forcing the subdomain, but I set the domain name up so that wouldn't be too feasible. So the real way to find the other app is to look at [cert transparency](https://www.certificate-transparency.org/) logs. So you can go to [crt.sh](https://crt.sh/?q=%25megafile.fun) to see these for the whole megafile.fun domain. This is a method many people have been using to find more attack surface for bug bounties and similar tasks. Certificate transparency is a great addition to TLS, but it means that you really cannot rely on hidden domain names if you're going to get a real, public cert for those domain names. So now we have the dev/testing version of Mega File which is abqtt.supersecret.dev-test.megafile.fun.

(3) Once you get to the dev app, you'll find a bunch of red herrings that don't mean anything (the serialized value as the CSRF token, the wide open CORS headers, the terrible CSP config and some other smaller goodies). As on the prod app, there is a way to get some source code, but only a couple files. You can get `/.report-uri.php.swp` and `/.functions.php.swp` which are all you really need from the dev server. These are vim swap files which allow anyone with access to read the contents of the original file. Not much of the rest of the code is different for this app. The swap files being exposed via the web browser is something that has been discussed over the years but most recently [brought up](http://seclists.org/oss-sec/2017/q4/145) by [Hanno Böck](https://blog.hboeck.de/) (a hacker we can all look up to) in the oss-sec mailing list. After looking at the code for report-uri.php, you should discover a url parameter that can be used but is not seen on the frontend. It wasn't made to be unguessable, so you technically don't need the source code to know to use the url parameter but it makes things a lot easier. The source code is needed for bypassing validation in the next part though.

(4) After examining report-uri.php you should be thinking about how you can break the domain name validation that's being done. This and the next part are both inspired heavily by [Orange Tsai's](http://blog.orange.tw/) [Def Con/Blackhat talk](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf) about SSRF. Another thing that you should notice from looking at the code, is that in functions.php there is a function `addRedisShare()` which gets called in `addShare()`. `addRedisShare()` connects to a redis instance and sends a message with the two user IDs to a channel. But back to the SSRF for now: the SSRF happens because of a discrepancy in parsing between php's `parse_url()` curl. So when validating the domain name from `parse_url()`, this can be bypassed so that the code will make an HTTP request to any resource you specify. There are a few things you could try with this, like hitting the prod web app from the dev server. But ultimately you'll need to find the web server listening locally on the dev server on port 8080. You could enumerate all the ports on the local server to find this, or you could try the common web service ports looking for something juicy. A payload to hit this internal API is 

```http
https://abqtt.supersecret.dev-test.megafile.fun/report-uri.php?url=http://foo@127.0.0.1:8080 @41da029b1352f8733d17f23def226ec4.report-uri.com/
```

Or urlencoded:

```http
https://abqtt.supersecret.dev-test.megafile.fun/report-uri.php?url=http%3A%2F%2Ffoo%40127.0.0.1%3A8080%20%4041da029b1352f8733d17f23def226ec4.report-uri.com%2F
```

This will make report-uri.php perform a GET request instead of POST since there's no POST body.

(5) Now you have to figure out how this internal service works. Looking at the result, you can determine that the returned page is the home page for Swagger documentation of a Flask API. To figure out how the API works, you can GET the /swagger.json from this service using the payload mentioned in the last section. There are a couple endpoints, but the one we care about is /configs. The Swagger documentation shows that we need to post to it with a paremeter called `url`, which we can assume is a URL the API will try to fetch in some way. In Orange's SSRF talk, he shows some slides about how some python libraries are vulnerable to CRLF injection. The talk also mentions protocol smuggling to Redis and Memcached specifically, which is exactly what is required in this case (with redis specifically). You must inject CRLF characters into the URL given to the Flask API in order to send commands to the redis server. From step 1 we know the host, port and password of the redis instance. And from step 4 we saw in `addRedisShare()` that we just need to send a message to the 'shares' channel on redis with a message of `<fromID> <toID>` to add any share relationship we'd like. Anything that can communicate with the Redis server is viewed as trusted so there are no checks on the share relationships that are placed here. The script `share_transfer.py` listens for messages to the 'shares' channel and then places valid share messages into the prod DB. So any share added to Redis will be replicated to the prod environment, which the message on the shares page of the dev site indicated. The double SSRF payload that combines steps 4 and 5 to add a share from nk-rocket-man (id of 2) to an id of 3 is:

```http
POST /report-uri.php?url=http%3A%2F%2Ffoo%40127.0.0.1%3A8080%20%4041da029b1352f8733d17f23def226ec4.report-uri.com%2Fconfigs%2F HTTP/1.1
Host: abqtt.supersecret.dev-test.megafile.fun
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36
Content-type: application/json
Content-Length: 222

url=http%3A%2F%2F172.31.38.50%0D%0A%20AUTH%20f2ca143fc4fd33f6dfcec811e4d19f3cb017a8b904535195037b970e401d0ce2fa40320b9169bafb38f08c5db216803a2f267f0f243b17c65bd48fae92dc3609%0D%0A%20publish%20shares%20%222%203%22%0D%0A%20%3A6379
```

When adding a share on the dev app, we really do have to be careful because if we add a share from nk-rocket-man to a user ID we don't own, another team could get access to the file. Assuming we shared things properly we can login with our account on the prod app and just use the app normally to view files shared to us by nk-rocket-man. He has a file called `message.txt` which has the flag. Simply clicking on the file to download should work fine, and then you have the flag.
