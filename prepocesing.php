<?php
ob_start();
session_start();
set_time_limit(300);

include "koneksi.php";

// Proses pemrosesan jika tombol diklik
if (isset($_POST['proses'])) {
    // Memanggil skrip Python untuk preprocessing
    $output = shell_exec("python proses_prepocesing.py");
    
    // Memastikan skrip Python telah berjalan dengan benar
    if ($output === null) {
        echo "Error menjalankan skrip Python.";
        exit;
    }

    // Menyimpan status pemrosesan ke sesi
    $_SESSION['proses_selesai'] = true;
}

// Mengambil hasil preprocessing dari database
$result = null;
if (isset($_SESSION['proses_selesai']) && $_SESSION['proses_selesai']) {
    $sql = "SELECT tweet_id, full_text, text_bersih FROM proses";
    $result = mysqli_query($conn, $sql);
}

// Proses penghapusan jika tombol diklik
if (isset($_POST['hapus'])) {
    // Menghapus isi tabel proses dari database
    $query_delete_data = "DELETE FROM proses";
    mysqli_query($conn, $query_delete_data);
    $_SESSION['proses_selesai'] = false;
    $result = null;
}
?>
<div class="card-header">
    <form method="post">
        <button type="submit" class="btn btn-primary" name="proses">Proses</button>
        <button type="submit" class="btn btn-danger" name="hapus">Hapus</button> <!-- Tombol hapus -->
    </form>
</div>
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <table id="datatable" class="basic-datatables table table-bordered dt-responsive"
                    style="border-collapse: collapse; border-spacing: 0; width: 100%;">
                    <thead>
                        <tr>
                            <th>tweet_id</th>
                            <th>full_text</th>
                            <th>text_bersih</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php
                        // Menampilkan hasil preprocessing
                        if (isset($result)) {
                            while ($row = mysqli_fetch_assoc($result)) {
                                ?>
                                <tr>
                                    <td class="col-1">
                                        <?= htmlspecialchars($row['tweet_id']); ?>
                                    </td>
                                    <td class="col-0">
                                        <?= htmlspecialchars($row['full_text']); ?>
                                    </td>
                                    <td class="col-0">
                                        <?= htmlspecialchars($row['text_bersih']); ?>
                                    </td>
                                </tr>
                                <?php
                            }
                        }
                        ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<?php
$title = "Preprocessing";
$page_title = "Preprocessing";
$content = ob_get_clean();
include 'layout.php';
?>
