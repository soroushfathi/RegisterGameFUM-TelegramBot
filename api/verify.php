<?php
/*
 * ZarinPal Advanced Class
 *
 * version 	: 1.0
 * link 	: https://vrl.ir/zpc
 *
 * author 	: milad maldar
 * e-mail 	: miladworkshop@gmail.com
 * website 	: https://miladworkshop.ir
*/

$base_url = "https://api.telegram.org/bot";
$token = "**************************8";

// database
$username = "***************";
$password = "****************";
$dbname = "*******************";
// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
    echo 'error';
  die("Connection failed: " . $conn->connect_error);
}

$price = 60000;
$chatid = "";
if(isset($_GET['price']) && isset($_GET['chatid'])){
	$price=$_GET['price'];
	$chatid=$_GET['chatid'];
}
require_once("zarinpal_function.php");

$MerchantID 	= "*****************************";
$Amount 		= intval($price);
$ZarinGate 		= false;
$SandBox 		= false;

$zp 	= new zarinpal();
$result = $zp->verify($MerchantID, $Amount, $SandBox, $ZarinGate);

if (isset($result["Status"]) && $result["Status"] == 100)
{
	// Success
	echo "تراکنش با موفقیت انجام شد";
	echo "<br />مبلغ : ". $result["Amount"];
	echo "<br />کد پیگیری : ". $result["RefID"];
// 	echo "<br />Authority : ". $result["Authority"];
	
    $msg = "تراکنش_موفق، پرداخت با موفقیت انجام شد و تیم شما فعال گردید✅";
    
	json_decode(file_get_contents($base_url.$token."/SendMessage?chat_id=".$chatid."&text=".$msg));
	

	
	$sql = "UPDATE Team SET statuspay = 1, authority = \"{$result["Authority"]}\", refId = \"{$result["RefID"]}\" WHERE code = \"{$chatid}\"";
    if ($conn->query($sql) === TRUE) {
        echo "paymant Team update successfully";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }
} else {
	// error
	echo "پرداخت ناموفق";
	echo "<br />کد خطا : ". $result["Status"];
	echo "<br />تفسیر و علت خطا : ". $result["Message"];
}