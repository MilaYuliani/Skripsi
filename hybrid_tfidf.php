<?php
session_start();
ob_start();
include "koneksi.php";

// Memproses data menggunakan skrip Python
if (isset($_POST['proses'])) {
    // Memanggil skrip Python untuk preprocessing dan perhitungan
    $output = shell_exec("python hybrid_tfidf.py");

    // Menyimpan status pemrosesan ke sesi
    $_SESSION['proses_selesai'] = true;
}

// Menghapus data dari database dan mengatur ulang AUTO_INCREMENT
if (isset($_POST['hapus'])) {
    $sql_delete = "DELETE FROM hybrid_tfidf";
    mysqli_query($conn, $sql_delete);

    // Mengatur ulang AUTO_INCREMENT
    $sql_reset_ai = "ALTER TABLE hybrid_tfidf AUTO_INCREMENT = 1";
    mysqli_query($conn, $sql_reset_ai);

    // Mengatur ulang status pemrosesan
    $_SESSION['proses_selesai'] = false;
    header("Location: " . $_SERVER['PHP_SELF']);
    exit;
}

// Mengambil kalimat utama per klaster
$sql_kalimat_percluster = "
    SELECT 
        cluster_id, 
        GROUP_CONCAT(text SEPARATOR ' ') AS best_percluster_text,
        MAX(W_S) AS best_percluster_ws
    FROM 
        hybrid_tfidf 
    WHERE 
        best_percluster = 1
    GROUP BY 
        cluster_id
";
$result_kalimat_percluster = mysqli_query($conn, $sql_kalimat_percluster);

// Menemukan kalimat dengan W_S tertinggi di seluruh klaster
$highest_ws_value = 0;
while ($row = mysqli_fetch_assoc($result_kalimat_percluster)) {
    if ($row['best_percluster_ws'] > $highest_ws_value) {
        $highest_ws_value = $row['best_percluster_ws'];
    }
}

// Kembalikan hasil pointer ke awal untuk iterasi tampilan
mysqli_data_seek($result_kalimat_percluster, 0);
?>

<div class="card-header">
    <div class="d-flex justify-content-between">
        <form method="post">
            <button type="submit" class="btn btn-primary" name="proses">Proses</button>
            <button type="submit" class="btn btn-danger" name="hapus">Hapus</button>
        </form>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Hasil Pembobotan</h5>
                <div class="table-responsive">
                    <table id="datatable-pembobotan" class="table table-bordered dt-responsive nowrap" style="width:100%">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Text</th>
                                <th>TF</th>
                                <th>IDF</th>
                                <th>TF*IDF</th>
                                <th>W_wi</th>
                                <th>W_S</th>
                                <th>nf_S</th>
                            </tr>
                        </thead>
                        <tbody>
                        <?php
                        // Mengambil hasil perhitungan pembobotan dan kalimat utama per cluster dari database
                        $sql_pembobotan = "SELECT * FROM hybrid_tfidf ORDER BY cluster_id"; // Query untuk hasil pembobotan
                        $result_pembobotan = mysqli_query($conn, $sql_pembobotan);
                        if (isset($result_pembobotan)) {
                            while ($row = mysqli_fetch_assoc($result_pembobotan)) {
                        ?>
                            <tr>
                                <td><?= $row['id']; ?></td>
                                <td><?= $row['text']; ?></td>
                                <td><?= $row['tf']; ?></td>
                                <td><?= $row['idf']; ?></td>
                                <td><?= $row['tfidf']; ?></td>
                                <td><?= $row['W_wi']; ?></td>
                                <td><?= $row['W_S']; ?></td>
                                <td><?= $row['nf_S']; ?></td>
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
</div>

<?php if (isset($result_kalimat_percluster) && mysqli_num_rows($result_kalimat_percluster) > 0): ?>
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Kalimat Utama Per Klaster</h5>
                    <div class="table-responsive">
                        <table id="datatable-kalimat-percluster" class="table table-bordered dt-responsive nowrap" style="width:100%">
                            <thead>
                                <tr>
                                    <th>ID Klaster</th>
                                    <th>Kalimat Utama</th>
                                    <th>Skor Bobot (W_S)</th>
                                </tr>
                            </thead>
                            <tbody>
                            <?php while ($row = mysqli_fetch_assoc($result_kalimat_percluster)): ?>
                                <tr>
                                    <td><?= $row['cluster_id']; ?></td>
                                    <td><?= $row['best_percluster_text']; ?></td>
                                    <td
                                        <?php if ($row['best_percluster_ws'] == $highest_ws_value): ?>
                                            style="color: red;"
                                        <?php endif; ?>
                                    >
                                        <?= $row['best_percluster_ws']; ?>
                                    </td>
                                </tr>
                            <?php endwhile; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
<?php else: ?>
    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Kalimat Utama Per Klaster</h5>
                    <p>Tidak ada kalimat utama per klaster yang ditemukan.</p>
                </div>
            </div>
        </div>
    </div>
<?php endif; ?>

<?php
$title = "hybrid_tfidf";
$page_title = "Hybrid TF-IDF";
$content = ob_get_clean();
include 'layout.php';
?>
