#!/usr/bin/env perl
use CGI;
use CGI::Cookie;

my $query = new CGI;

#set up initial content type and output values
my $contentType = "text/plain";
my $output = "Hmmm..bad filename";

#get the name of the image from the GET param
my $xml_base_dir = "/var/www/megafile/xml_uploads/";
my $filename = $xml_base_dir . $query->param('name');
# print "Content-type: " . $contentType . "\r\n\r\n";

my $username = get_username();

#get the image if it's legit and do our cool stats on it
if($username ne "" && is_supported_file($filename, $username) && is_supported_path($filename) && -r $filename) {
	# gen_stats($filename); #probs don't need this now, woo!
	# my $extension = get_image_type($filename);

	# remove any null bytes from filename so it doesn't mess with our syscalls ;)
	@bits = split /\0/, $filename;
	$filename = $bits[0];

	# this method may be too slow or memory consuming. see: http://www.perlmonks.org/?node_id=1952
	local $/ = undef; #this unsets the Input Record Separator to make <> give me the whole file at once
	open my $slurp, "<$filename" or die "error opening file: $!";
    binmode ($slurp, ':raw');
    $output = <$slurp>;
    close $slurp;
    chomp($output);

	$contentType = "text/xml";
}

#print out the response
print "Content-type: " . $contentType . "\r\n\r\n";
print $output;


sub get_username() {
	%cookies = CGI::Cookie->fetch;
	$session = $cookies{'PHPSESSID'}->value;
	if($session eq "" || $session !~ /^[a-zA-Z0-9]+$/) {
		return "";
	}

	$contents = `curl 'http://127.0.0.1/username.php' -H 'Cookie: PHPSESSID=$session'`;
	@lines = split /:/, $contents;
	if($lines[0] eq "username") {
		if($lines[1] ne "") {
			return $lines[1];
		}
	}

	return "";
}

sub is_supported_file {
    my ($path, $user) = @_;
    print "user: '$user'\n";

    my $result = 0;
    if ($path =~ /$user\.xml$/i) {
        return 1;
    }

    return 0;
}

sub is_supported_path {
	my ($path) = @_;

	if($path =~ m|^/var/www/megafile/xml_uploads|) {
		return 1;
	}

	return 0;
}

sub gen_stats {
	# cool stats things yay
	return;
}
