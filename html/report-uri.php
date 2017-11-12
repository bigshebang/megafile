<?php

header('Content-Type: text/plain');

// print_r($_POST);

// $report = file_get_contents('php://input');
// print_r($report);
// print "\n";
// die();

### URI setup with CURL and validation###
//$uri = "127.0.0.1\r\nfoo";
//$uri = "http://lukemat.com/test";
#$uri = "http://google.com#@127.0.0.1";
#$uri = "http://127.0.0.1:11211:80";
#$uri = "http://127.0.0.1:11211#@google.com:80/";
#$uri = "http://foo@evil.com:80 @google.com";
#$uri = "http://foo@127.0.0.1:8080 @report-uri.com/swagger.json";
#$uri = "http://foo@127.0.0.1:8080 @google.com/configs/";
$uri = "https://41da029b1352f8733d17f23def226ec4.report-uri.com/r/d/csp/reportOnly";

if(isset($_GET['url'])){
	$temp_url = trim($_GET['url']);
	if($temp_url != ""){
		$uri = $temp_url;
	}
}

$parsed = parse_url($uri);
/*
var_dump($parsed);
echo "original URI: $uri \n";
echo "host: " . $parsed['host'] . "\n";
echo "port: " . $parsed['port'] . "\n";
*/

//Don't want any tricky users redirecting our CSP reports somewhere else!
$approved_host = "41da029b1352f8733d17f23def226ec4.report-uri.com";
$approved_scheme_prefix = "http";
$scheme = substr($parsed['scheme'], 0, strlen($approved_scheme_prefix));
if($scheme === $approved_scheme_prefix && $parsed['host'] == $approved_host){
	$ch = curl_init($uri);
} else {
	echo "invalid report URI";
	return;
}

### Body and POST setup ###
# if we got a non-empty report POST'd as JSON, POST it to report-uri otherwise do nothing
$report = file_get_contents('php://input');
if($report != ""){
	#set up curl by adding URI and JSON report to the body
	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, $report);
} else {
	echo "Error: must include the report in the body as JSON.";
}

//make curl call
$result = curl_exec($ch);

//gotta check for dem errors
if(!$result){
	echo "Seems like there was an issue.\n";
	// print curl_error($ch);
} else {
	echo "reported!\n";
}

//closerino the curl object
curl_close($ch);


?>