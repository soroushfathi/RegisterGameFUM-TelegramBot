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

$name = $_POST["name"];
$code = $_POST["code"];
// mysqli_query($conn, 'set names "utf8"');
$sql = "INSERT INTO Team (code, name, membercount, score) VALUES (\"{$code}\", \"{$name}\", 1, 0)";


if ($conn->query($sql) === TRUE) {
  echo "New record created successfully";
} else {
  echo "Error: " . $sql . "<br>" . $conn->error;
}


// echo $name;
// $sql = "INSERT INTO Team (code, name, membercount, score) VALUES (".$code.", ".$name.", 1, 0)";
// echo $name;
// $result = mysqli_query($conn, $sql);
// echo $result;
// $result = $conn->query($sql);
// echo $result;

return $result;

?>