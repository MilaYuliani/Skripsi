<?php

require 'vendor/autoload.php';

use PhpOffice\PhpSpreadsheet\IOFactory;

// Membuat koneksi database
$pdo = new PDO('mysql:host=localhost;dbname=databanjir', 'root', '');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Cek jika file telah diupload
if ($_FILES['excel_file']['error'] == 0) {
    $inputFileName = $_FILES['excel_file']['tmp_name'];  // Temp file name
    $reader = IOFactory::createReaderForFile($inputFileName);
    $spreadsheet = $reader->load($inputFileName);

    $sheetData = $spreadsheet->getActiveSheet()->toArray();
    $sheetData = array_slice($sheetData, 1);
    foreach ($sheetData as $row) {
        // Sesuaikan indeks array dengan struktur file Excel Anda
        $conversation_id_str = $row[0];
        $created_at = date("Y-m-d H:i:s", strtotime($row[1])); // Ubah format tanggal;
        $favorite_count = $row[2];
        $full_text = $row[3];
        $id_str = $row[4];
        $image_url = $row[5];
        $in_reply_to_screen_name = $row[6];
        $lang = $row[7];
        $location = $row[8];
        $quote_count = $row[9];
        $reply_count = $row[10];
        $retweet_count = $row[11];
        $tweet_url = $row[12];
        $user_id_str = $row[13];
        $username = $row[14];

        // Query untuk memasukkan data
        $sql = "INSERT INTO datacraw (conversation_id_str, created_at, favorite_count, full_text, id_str, image_url, in_reply_to_screen_name, lang, location, quote_count, reply_count, retweet_count, tweet_url, user_id_str, username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([$conversation_id_str, $created_at, $favorite_count, $full_text, $id_str, $image_url, $in_reply_to_screen_name, $lang, $location, $quote_count, $reply_count, $retweet_count, $tweet_url, $user_id_str, $username]);
    }

    header("location: " . $_SERVER['HTTP_REFERER']);
} else {
    echo "Error: " . $_FILES['excel_file']['error'];
}
?>
