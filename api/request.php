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
$price = 60000;
$chatid = "";
if(isset($_GET['price']) & isset($_GET['chatid'])){
	$price=$_GET['price'];
	$chatid=$_GET['chatid'];
}
require_once("zarinpal_function.php");

$MerchantID 	= "******************************";
$Amount 		= intval($price);
$Description 	= "تراکنش زرین پال - اتاق فرار فردوسی";
$Email 			= "";
$Mobile 		= "";
$CallbackURL 	= "*********************?chatid=".$chatid."&price=".$price;
$ZarinGate 		= false;
$SandBox 		= false;

$zp 	= new zarinpal();
$result = $zp->request($MerchantID, $Amount, $Description, $Email, $Mobile, $CallbackURL, $SandBox, $ZarinGate);

if (isset($result["Status"]) && $result["Status"] == 100)
{
	// Success and redirect to pay
	$zp->redirect($result["StartPay"]);
} else {
	// error
	echo "خطا در ایجاد تراکنش";
	echo "<br />کد خطا : ". $result["Status"];
	echo "<br />تفسیر و علت خطا : ". $result["Message"];
}