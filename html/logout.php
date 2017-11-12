<?php 

session_start();
session_unset();
setcookie("CSRF_TOKEN", "", 1);
header('Location: /');
die();

?>
