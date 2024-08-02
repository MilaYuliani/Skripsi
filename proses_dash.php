<?php

// Fungsi untuk membuat koneksi ke database
function createConnection() {
    $servername = "localhost";
    $username = "root";
    $password = "";
    $dbname = "databanjir";

    $conn = new mysqli($servername, $username, $password, $dbname);

    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

    return $conn;
}

// Fungsi untuk mengambil data dari database
function fetchDataFromDatabase($conn)
{
    // Query untuk mengambil jumlah data asli dari tabel datacraw
    $data_asli_query = "SELECT COUNT(*) as total FROM datacraw";

    // Query untuk mengambil jumlah data bersih dari tabel proses
    $data_bersih_query = "SELECT COUNT(*) as total FROM proses";

    // Query untuk mengambil jumlah data model dari tabel model
    $data_model_query = "SELECT COUNT(*) as total FROM model";

    // Query untuk mengambil jumlah cluster yang terbentuk dari tabel clusters
    $cluster_query = "SELECT COUNT(DISTINCT cluster_id) as total FROM clusters";

    // Eksekusi query untuk mendapatkan jumlah data asli
    $data_asli_result = $conn->query($data_asli_query);
    if (!$data_asli_result) {
        die("Error fetching data asli: " . $conn->error);
    }

    // Eksekusi query untuk mendapatkan jumlah data bersih
    $data_bersih_result = $conn->query($data_bersih_query);
    if (!$data_bersih_result) {
        die("Error fetching data bersih: " . $conn->error);
    }

    // Eksekusi query untuk mendapatkan jumlah data model
    $data_model_result = $conn->query($data_model_query);
    if (!$data_model_result) {
        die("Error fetching data model: " . $conn->error);
    }

    // Eksekusi query untuk mendapatkan jumlah cluster yang terbentuk
    $cluster_result = $conn->query($cluster_query);
    if (!$cluster_result) {
        die("Error fetching cluster data: " . $conn->error);
    }

    // Ambil jumlah data asli dari hasil query
    $data_asli = $data_asli_result->fetch_assoc()['total'];

    // Ambil jumlah data bersih dari hasil query
    $data_bersih = $data_bersih_result->fetch_assoc()['total'];

    // Ambil jumlah data model dari hasil query
    $data_model = $data_model_result->fetch_assoc()['total'];

    // Ambil jumlah cluster dari hasil query
    $cluster_count = $cluster_result->fetch_assoc()['total'];

    // Return array berisi jumlah data asli, bersih, model, dan cluster
    return array(
        'data_asli' => $data_asli,
        'data_bersih' => $data_bersih,
        'data_model' => $data_model,
        'cluster_terbentuk' => $cluster_count
    );
}

// Jika permintaan 'getData' diterima, tangani dengan mengambil data dari database dan mengembalikan respons dalam format JSON
if (isset($_GET['action']) && $_GET['action'] == 'getData') {
    // Buat koneksi ke database
    $conn = createConnection();

    // Ambil data dari database
    $data = fetchDataFromDatabase($conn);

    // Tutup koneksi ke database
    $conn->close();

    // Kembalikan data dalam format JSON
    echo json_encode($data);
    exit(); // Keluar dari skrip setelah mengembalikan respons
}

?>
