<?php

#some config options that don't need to be in the config file
$BASE_WEB_DIR = "/var/www/megafile/";
$HTML_DIR = "html/";
$CGI_BIN_DIR = "cgi-bin/";
$XML_EXAMPLES_DIR = $HTML_DIR . "xml/";
$XML_UPLOADS_DIR = "xml_uploads/";
$VALID_USERNAME = "/^[a-zA-Z0-9\-_]+$/";
$CSRF_TOKEN = "ca969a1bc97732d97b1e88ce8396c216";

function connect_to_db($find = 0){
	$db_config = parse_ini_file("../config.dev.ini", true)['sql']; #get settings from config file

	//need to determine which user we need here so we get the right user and pass
	//TODO: change these from numbers to strings
	$usertype = "";
	if($find == 1)
		$usertype = "_upload";
	else if($find == 2)
		$usertype = "_del";
	else if($find == 3)
		$usertype = "_dev";

	return new mysqli(
		$db_config['host'],
		$db_config['db' . $usertype . '_user'],
		$db_config['db' . $usertype . '_password'],
		$db_config['db'],
		$db_config['port']
	);
}

function set_login_session_values($id, $username, $first){
	$_SESSION['id'] = $id;
	$_SESSION['username'] = $username;
	$_SESSION['first'] = $first;

	#set CSRF token as a cookie
	$is_secure = 0;
	if($_SERVER['HTTPS'])
		$is_secure = 1;

	setcookie("CSRF_TOKEN", getCsrfToken($id), $secure=$is_secure);
}

function register_user($conn, $username, $password, $first, $last, $admin = 0){
	//setup prepared statement
	$statement = $conn->prepare("INSERT INTO users (username, password, first, last, admin) VALUES (?, ?, ?, ?, ?)");

	//generate hash and session ID
    $pass = hash("sha512", $username . $password);

	//bind params to prepared statement, execute query
	$statement->bind_param("ssssi", $username, $pass, $first, $last, $admin);
	$statement->execute();
    if($statement->error)
        $result = $statement->error."<br />"; #.$sql;
    else
        $result = $statement->insert_id;

	$statement->close();
    return $result;
}

function check_user($conn, $username){
	$statement = $conn->prepare("SELECT * FROM users WHERE username = ?");
	$statement->bind_param("s", $username);
	$statement->execute();

    $result = $statement->get_result();
    echo $statement->error;

    if($result->num_rows > 0)
        return True; 
    else
        return False;
}

function login_user($conn, $username, $ptpass){
    $password = hash("sha512", $username . $ptpass);
	$statement = $conn->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
	$statement->bind_param("ss", $username, $password);
	$statement->execute();
	$query = $statement->get_result();
    $error = $statement->error;

	if($error){
        $result = $error;
        return $result;
    }
    if ($query->num_rows > 0) {
        $result = $query->fetch_array(MYSQLI_ASSOC);
        //$result = $query;
        $query->free();
    }
    else
        $result = False;

	return $result;
}

function get_info($conn, $id){
	if($id == "")
	{
		$result['error'] = "ID must not be blank.";
		return $result;
	}

	$statement = $conn->prepare("SELECT * FROM users where id = ?");
	$statement->bind_param("s", $id);
	$statement->execute();
	$query = $statement->get_result();
    $error = $statement->error;

	if($error)
	{
		$result['error'] = $error;
		return $result;
	}

    $result = $query->fetch_array(MYSQLI_ASSOC);
    $query->free();
    return $result;
}

function lookup_user($conn, $id){
    if(is_numeric($id))
	{
		$statement = $conn->prepare("SELECT id, username FROM users WHERE id = ?");
		$statement->bind_param("i", $id);
	}
    else
	{
		$statement = $conn->prepare("SELECT id, username FROM users WHERE "
									. "username LIKE ?");
		$id = "%" . $id . "%";
		$statement->bind_param("s", $id);
	}

	$statement->execute();
	$error = $statement->error;
	$result = $statement->get_result();
	$statement->close();

	return array($result, $error);
}

function getFiles($conn, $requesterID, $ownerID)
{
	//if either ID is zero, that's a problem. there are no IDs of 0
	$requesterID = intval($requesterID);
	$ownerID = intval($ownerID);
	if($requesterID === 0 || $ownerID === 0)
	{
		$error = "bad ID";
		return array("", $error);
	}

	//if the user isn't requesting to see their file list, make sure they allowed to see what
	//they're requesting
	if($requesterID !== $ownerID)
	{
		//check if the requested account is sharing with the requesting account
		$isSharing = checkShare($conn, $ownerID, $requesterID);
		if($isSharing === 0)
		{
			$error = "Hmm..that doesn't seem right";
			return array("", $error);
		}
	}

	$statement = $conn->prepare("SELECT id,name,size FROM files WHERE userid = ?");
	$statement->bind_param("i", $ownerID);
	$statement->execute();

	$error = $statement->error;
	$result = $statement->get_result();
	$statement->close();

	return array($result, $error);
}

function getFile($conn, $requesterID, $fileid)
{
	$isAuthorized = authorizedForFile($conn, $requesterID, $fileid);
	$result = "";
	$error = "";

	if($isAuthorized === 1)
	{
		$statement = $conn->prepare("SELECT * FROM files WHERE id = ?");
		$statement->bind_param("i", $fileid);
		$statement->execute();

		$error = $statement->error;
		$result = $statement->get_result()->fetch_array();
		$statement->close();
	}
	else
	{
		$error = "File not found";
	}

	return array($result, $error);
}

function authorizedForFile($conn, $requesterID, $fileid)
{
	$notAuthorized = 0;
	$authorized = 1;

	#check if the requesting ID has access to this file
	#this means we check if the requesting ID owns the file first
	$statement = $conn->prepare("SELECT id, userid from files WHERE id = ?");
	$statement->bind_param("i", $fileid);
	$statement->execute();
	$error = $statement->error;
	$result = $statement->get_result();
	$statement->close();

	//if any error given, fail closed
	if($error)
		return $notAuthorized;

	//if there was a problem with the connection, fail closed
	if(!$result)
		return $notAuthorized;

	//get the owner of the requested file
	$row = $result->fetch_assoc();
	$ownerID = intval($row['userid']);
	$requesterID = intval($requesterID);

	//if requesterID is zero, that's a problem. there are no IDs of 0
	if($requesterID === 0)
		return $notAuthorized;

	//check if the requester owns the file
	if ($ownerID === $requesterID)
		return $authorized;

	//check if the owner is sharing files with the requester
	$isSharing = checkShare($conn, $ownerID, $requesterID);
	if($isSharing === 1)
		return $authorized;

	return $notAuthorized;
}

function addShare($conn, $fromID, $toID)
{
	//if fromID is zero, that's a problem. there are no IDs of 0
	$fromID = intval($fromID);
	if($fromID === 0)
		return "Hmm..something doesn't seem right";

	if($fromID === intval($toID))
		return "Cannot share files with yourself.";

	//make sure not already sharing
	$alreadySharing = checkShare($conn, $fromID, $toID);
	if($alreadySharing === 1)
		return "You are already sharing files with this user.";

	$statement = $conn->prepare("INSERT INTO shares (ownerid, shareid) VALUES(?, ?)");
	$statement->bind_param("ii", $fromID, $toID);
	$statement->execute();

	$error = $statement->error;
	$statement->close();

	# add the share to redis to test prod integration
	$result = addRedisShare($myID, $theirID);

	//if the function returned anything, add it to the error
	if($result != "")
	{
		//don't overwrite existing error, just tack onto it
		if($error != "")
			$error .= "\n" . $result;
		else
			$error = $result;
	}

	return $error;
}

function addRedisShare($myID, $theirID)
{
	$redis_config = parse_ini_file("../config.dev.ini", true)['redis']; #get settings from config file
	$redis_timeout = 5;

	$redis = new Redis();
	$connectResult = $redis->connect($redis_config['host'], $redis_config['port'], $redis_timeout);
	if(!$connectResult)
		return "Cannot connect to redis";

	$authResult = $redis->auth($redis_config['password']);
	if(!$authResult)
		return "Cannot connect to redis";

	$share = $myID . " " . $theirID;
	$redis->publish($redis_config['channel'], $share);

	return "";

//checks to see if fromID is sharing to toID
function checkShare($conn, $fromID, $toID)
{
	//if fromID is zero, that's a problem. there are no IDs of 0
	//technically this should never be called without being checked, but let's be safe
	$fromID = intval($fromID);
	if($fromID === 0)
		return 0;

	//if the user is the same, technically they're "sharing"
	//shouldn't get here, but let's be safe. and lack of time to test
	if($fromID === intval($toID))
		return 1;

	$statement = $conn->prepare("SELECT * FROM shares WHERE ownerid = ? AND "
								. "shareid = ?");
	$statement->bind_param("ii", $fromID, $toID);
	$statement->execute();
	$rows = $statement->get_result()->num_rows;
	$statement->close();

	if($rows > 0)
		return 1;
	else
		return 0;
}

function getShares($conn, $myID)
{
	$statement = $conn->prepare("SELECT ownerid FROM shares WHERE shareid = ?");
	$statement->bind_param("i", $myID);
	$statement->execute();

	$error = $statement->error;
	$result = $statement->get_result();
	$statement->close();

	return array($result, $error);
}

function getMyShares($conn, $myID)
{
	$statement = $conn->prepare("SELECT shareid FROM shares WHERE ownerid = ?");
	$statement->bind_param("i", $myID);
	$statement->execute();

	$error = $statement->error;
	$result = $statement->get_result();
	$statement->close();

	return array($result, $error);
}

function deleteFile($filename, $ownerid)
{
	$tempConn = connect_to_db(2);
	$statement = $tempConn->prepare("DELETE FROM files WHERE name = ? AND "
									. "userid = ?");
	$statement->bind_param("si", $filename, $ownerid);
	$statement->execute();
	$error = $statement->error;
	$statement->close();

	return $error;
}

function deleteShare($ownerid, $shareid)
{
	$tempConn = connect_to_db(2);
	$statement = $tempConn->prepare("DELETE FROM shares WHERE ownerid = ? AND "
									. "shareid = ?");
	$statement->bind_param("ii", $ownerid, $shareid);
	$statement->execute();
	$error = $statement->error;
	$statement->close();

	return $error;
}

function getSize($conn, $userid)
{
	$statement = $conn->prepare("SELECT sum(size) as sum FROM files WHERE "
								. "userid = ?");
	$statement->bind_param("i", $userid);
	$statement->execute();

	$error = $statement->error;
	$result = $statement->get_result()->fetch_array();
	$statement->close();

	if($error)
		return $error;
	else
		return intval($result['sum']);
}

function updateUser($first, $last, $bio, $userid)
{
	$newConn = connect_to_db(1);
	$statement = $newConn->prepare("UPDATE users SET first = ?, last = ?, "
								   . "bio = ? WHERE id = ?");
	$statement->bind_param("sssi", $first, $last, $bio, $userid);
	$statement->execute();
	$newConn->close();

	$error = $statement->error;
	$statement->close();

	return $error;
}

function addFile($conn, $filename, $filetype, $filesize, $contents, $myID)
{
	//check to see if file with the same name exists, if it does, then we update that
	$statement = $conn->prepare("SELECT * FROM files where name = ? AND userid = ?");
	$statement->bind_param("si", $filename, $myID);
	$statement->execute();
	$error = $statement->error;
	$result = $statement->get_result();
	$statement->close();

	if($error)
		return $error;

	//update existing file
	if($result->num_rows > 0)
	{
		$newConn = connect_to_db(1);
		$statement = $newConn->prepare("UPDATE files SET type = ?, size = ?, content = ? WHERE userid = ? AND name = ?");
		$statement->bind_param("sisis", $filetype, $filesize, $contents, $myID, $filename);
	}
	else //adding new file
	{
		$statement = $conn->prepare("INSERT INTO files (name, type, size, content, userid) VALUES (?, ?, ?, ?, ?)");
		$statement->bind_param("ssisi", $filename, $filetype, $filesize, $contents, $myID);
	}

	$statement->execute();
	$error = $statement->error;
	$statement->close();

	if(isset($newConn))
		$newConn->close();

	return $error;
}

function execute_sql($conn, $query)
{
	$results = $conn->query($query);

	$error = $conn->error;
	$result = $results;

	return array($result, $error);
}

function logXmlUpload($conn, $upload, $id)
{
	//Get file contents. reduce size if larger than our DB allowed max
	$file_size = $upload['size'];
	if(intval($file_size) > 8191)
		$file_size = 8191;

	$f = fopen($upload['tmp_name'], "r");
	$contents = fread($f, $file_size);
	fclose($f);

	//get the client's ip
	$ip = getClientIp();

	//setup prepared statement, bind and execute. don't care about errors
	$statement = $conn->prepare("INSERT INTO xml_uploads (contents, ip, uploader_id) VALUES (?, ?, ?)");
	$statement->bind_param("sss", $contents, $ip, $id);
	$statement->execute();
	$statement->close();
}

function getCsrfToken($id)
{
	global $CSRF_TOKEN;
	$csrf = array();
	$csrf["token"] = $CSRF_TOKEN;
	$csrf['id'] = $id;

	return serialize($csrf);
}

function getClientIp() {
    $ipaddress = '';
    if (array_key_exists('HTTP_CLIENT_IP', $_SERVER) && $_SERVER['HTTP_CLIENT_IP'])
        $ipaddress = $_SERVER['HTTP_CLIENT_IP'];
    else if(array_key_exists('HTTP_X_FORWARDED_FOR', $_SERVER) && $_SERVER['HTTP_X_FORWARDED_FOR'])
        $ipaddress = $_SERVER['HTTP_X_FORWARDED_FOR'];
    else if(array_key_exists('HTTP_X_FORWARDED', $_SERVER) && $_SERVER['HTTP_X_FORWARDED'])
        $ipaddress = $_SERVER['HTTP_X_FORWARDED'];
    else if(array_key_exists('HTTP_FORWARDED_FOR', $_SERVER) && $_SERVER['HTTP_FORWARDED_FOR'])
        $ipaddress = $_SERVER['HTTP_FORWARDED_FOR'];
    else if(array_key_exists('HTTP_FORWARDED', $_SERVER) && $_SERVER['HTTP_FORWARDED'])
        $ipaddress = $_SERVER['HTTP_FORWARDED'];
    else if(array_key_exists('REMOTE_ADDR', $_SERVER) && $_SERVER['REMOTE_ADDR'])
        $ipaddress = $_SERVER['REMOTE_ADDR'];
    else
        $ipaddress = 'UNKNOWN';
    return $ipaddress;
}

?>
