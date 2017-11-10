<?php
session_start();
if(!isset($_SESSION['id']))
{
	header("Location: /");
	die();
}

echo "username:" . $_SESSION['username'];

?>