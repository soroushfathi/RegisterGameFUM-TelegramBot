<?php

$servername = "localhost";
$username = "***************";
$password = "****************";
$dbname = "*******************";
// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);


// Check connection
if ($conn->connect_error) {
    echo 'error';
  die("Connection failed: " . $conn->connect_error);
}


$teamcode = $_POST["teamcode"];
$level = $_POST["level"];
$starttime = $_POST["starttime"];

// mysqli_query($conn, 'set names "utf8"');
$sql = "INSERT INTO level (teamcode, level, starttime) VALUES (\"{$teamcode}\", \"{$level}\", \"{$starttime}\")";
if ($conn->query($sql) === TRUE) {
  echo "New player created successfully";
} else {
  echo "Error: " . $sql . "<br>" . $conn->error;
}


?>