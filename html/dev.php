<?php
session_start();
if(!isset($_SESSION['id']))
{
	header("Location: /login.php");
	die;
}


function getElement($value, $err)
{
	$element = <<<TOP
			<li class="list-group-item">
			<div class="left" id="username-div"
TOP;
	if($err != "")
	{
		$element .= " style=\"color: red; margin-bottom: 11px;\">" . $err . "\n";
		$element .= <<<BOTTOM
			</div>
			<div class="clearfix"></div>
			</li>

BOTTOM;
	}
	else
	{
		$element .= <<<BOTTOM
			>$value
			</div>
			<div class="clearfix"></div>
			</li>

BOTTOM;
	}

	return $element;
}


require_once("functions.php");
$dev_conn = connect_to_db(3); #get that nice dev SQL user
$results = "";
$success = "";
$error = "";

if(isset($_POST['sql']) && $_POST['sql'] != "")
{
	if(!strpos($_POST['sql'], 'DROP') && !strpos($_POST['sql'], 'DELETE'))
	{
		$result = execute_sql($dev_conn, $_POST['sql']);

		$results = <<<TOP
				<br /><br />
				<div id="search-results">
				<h3 class="bars">Results</h3>
				<ul class="list-group" style="text-align: left;">

TOP;

			if($result[1] != "")
			{
				$results .= getElement("", "Error in the query.");
			}
			else
			{
				if($result[0]->num_rows < 1)
				{
					$results .= getElement("", "No rows returned.");
				}
				else
				{
					// $i = 0;
					$row = $result[0]->fetch_assoc();
					print "row: ";
					print_r($row);
					print "\n<br>";
					$columns = array();
					$rowStr = "";

					#gotta get the columns!
					foreach($row as $key => $value)
						array_push($columns, $key);

					# add each row that isn't at the end
					for($iterator = 0; $iterator < count($columns) - 1; $iterator++)
						$rowStr .= $columns[$iterator] . ", ";

					$rowStr .= $columns[$iterator]; //add the final column with no more commas

					$results .= getElement($rowStr, "");
					//add all the resultant rows
					do
					{
						$rowStr = "";

						for($iterator = 0; $iterator < count($columns) - 1; $iterator++)
							$rowStr .= $row[$columns[$iterator]] . ", ";

						$rowStr .= $row[$columns[$iterator]]; //add the final column with no more commas

						$results .= getElement($rowStr, "");
					} while($row = $result[0]->fetch_assoc());
				}
			}

			$result[0]->close(); //close mysqli_result bc we're done with it now

				$results .= <<<BOTTOM
				</ul>
				</div>

BOTTOM;
	}
	else
	{
		$sqlError = "you can't remove data; security violation. <a href=\"https://i.imgur.com/TkYVQWK.png\">BOO NOT COOL</a>.";
	}
}

$dev_conn->close();
?>
<!doctype html>
<html>
<head>
<title>Share Files - Mega File</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<script type="application/x-javascript"> addEventListener("load", function() { setTimeout(hideURLbar, 0); }, false); function hideURLbar(){ window.scrollTo(0,1); } </script>
<!--flexslider-css-->
<!--bootstrap-->
<link href="css/bootstrap.min.css" rel="stylesheet" type="text/css">
<!--coustom css-->
<link href="css/style.css" rel="stylesheet" type="text/css"/>
<!--fonts-->
<link href='http://fonts.googleapis.com/css?family=Open+Sans:400,300,300italic,400italic,800italic,800,700italic,700,600,600italic' rel='stylesheet' type='text/css'>
<!--/fonts-->
<!--script-->
<script src="js/jquery.min.js"> </script>
	<!-- js -->
		 <script src="js/bootstrap.js"></script>
	<!-- js -->
		<script type="text/javascript" src="js/move-top.js"></script>
<script type="text/javascript" src="js/easing.js"></script>
<!--/script-->
<script type="text/javascript">
			jQuery(document).ready(function($) {
				$(".scroll").click(function(event){		
					event.preventDefault();
					$('html,body').animate({scrollTop:$(this.hash).offset().top},900);
				});
			});
</script>
<script type="text/javascript"> 
	function submitform(i){
		var f = document.shareFiles;
		if(f.tagName == "FORM")
			f.submit();
		else
			f[i].submit();
	} 
</script>
<!--/script-->
	</head>
	<body>
		<div class="header" id="home">
			<?php
			require_once("menu.php");
			?>
			<div class="header-banner">
					<!-- Top Navigation -->
					<section class="bgi banner5"><h2>Share Files</h2> </section>
					
	<!-- contact -->
	<div class="contact-top">
		<!-- container -->
		<div style="width: 600px; text-align: center;" class="container">
			<div style="margin: 0 0 2.3em 0" class="mail-grids">
				<div style="float: none; width: 100%; padding-right: 15px;" class="col-md-6 contact-form">
					<p style="margin-bottom: 25px;">See what's in the shares table (build your own queries)</p>
					<form action="dev.php" method="POST">
						<input maxlength="128" type="text" name="sql" placeholder="SELECT * FROM shares;">
						<input type="submit" value="Execute">
					</form>
				</div>
				<div class="clearfix"> </div>
			<?php
			if($error)
			{
				// $safeError = htmlentities($error);
				echo <<<ERROR
				<div style="margin-top: 30px;">
				<p style="color: red;">$error</p>
				</div>

ERROR;
			}
			else if($success)
			{
				echo <<<ERROR
				<div style="margin-top: 30px;">
				<p style="color: green;">$success</p>
				</div>

ERROR;
			}
			else if($results)
			{
				echo $results . "\n";
			}
			?>
			</div>
		</div>
		<!-- //container -->
	</div>
	<!-- //contact -->
		</div>
</div>
<?php
require_once("footers.html");
?>
