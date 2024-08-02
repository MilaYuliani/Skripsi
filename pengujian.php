<?php
ob_start();

// Koneksi ke database MySQL
$conn = mysqli_connect("localhost", "root", "", "databanjir");

if (isset($_POST['proses'])) {
    // Memanggil skrip Python untuk preprocessing dan menghitung purity
    $output = [];
    exec("python purity.py 2>&1", $output);

    // Memisahkan nilai-nilai purity dari output skrip Python
    $overall_purity_all = isset($output[0]) ? floatval($output[0]) : 0;
    $overall_purity_200_random = isset($output[1]) ? floatval($output[1]) : 0;
    $overall_purity_100_random = isset($output[2]) ? floatval($output[2]) : 0;

    // Memanggil hasil dari tabel purity_results setelah proses Python
    $sql_purity_cluster = "SELECT cluster_id, purity, quality, jumlah_tweet FROM purity_results";
    $result_purity_cluster = mysqli_query($conn, $sql_purity_cluster);
} else {
    // Jika tidak ada proses Python, tetap menampilkan data yang ada di tabel
    $sql_purity_cluster = "SELECT cluster_id, purity, quality, jumlah_tweet FROM purity_results";
    $result_purity_cluster = mysqli_query($conn, $sql_purity_cluster);
}

if (isset($_POST['hapus'])) {
    // Menghapus isi tabel purity_results dari database
    $query_delete_data = "DELETE FROM purity_results";
    mysqli_query($conn, $query_delete_data);
    $result_purity_cluster = null;
}

// Menghitung total purity dan rata-rata purity
$total_purity = 0;
$average_purity = 0;
$total_purity_300 = 0; // Total purity untuk jumlah dokumen 300
$total_purity_200 = 0; // Total purity untuk jumlah dokumen 200
$total_purity_100 = 0; // Total purity untuk jumlah dokumen 100
$total_tweets = 0;
$num_clusters = 0;
$clusters_baik = [];
$clusters_buruk = [];

if (isset($result_purity_cluster) && mysqli_num_rows($result_purity_cluster) > 0) {
    while ($row = mysqli_fetch_assoc($result_purity_cluster)) {
        $num_clusters++;
        $total_tweets += $row['jumlah_tweet'];
        $total_purity += $row['purity'] * $row['jumlah_tweet'];

        // Menghitung total purity berdasarkan jumlah dokumen
        switch ($row['jumlah_tweet']) {
            case 300:
                $total_purity_300 += $row['purity'] * $row['jumlah_tweet'];
                break;
            case 200:
                $total_purity_200 += $row['purity'] * $row['jumlah_tweet'];
                break;
            case 100:
                $total_purity_100 += $row['purity'] * $row['jumlah_tweet'];
                break;
            default:
                // default case, jika jumlah dokumen tidak sesuai dengan yang diharapkan
                break;
        }

        // Mengklasifikasikan kluster ke dalam baik atau buruk
        if ($row['purity'] * 100 > 50) {
            $clusters_baik[] = $row['cluster_id'];
        } else {
            $clusters_buruk[] = $row['cluster_id'];
        }
    }
    $average_purity = $total_purity / $total_tweets;
    // Reset result set pointer for later use
    mysqli_data_seek($result_purity_cluster, 0);
} else {
    $average_purity = 0;
    $total_purity = 0;
}

?>

<div class="card-header">
    <div class="d-flex justify-content-between">
        <form method="post">
            <button type="submit" class="btn btn-primary" name="proses">Hasil</button>
            <button type="submit" class="btn btn-danger" name="hapus">Hapus</button> <!-- Tombol hapus -->
        </form>
    </div>
</div>
<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Purity per Cluster</h5>
                <table id="datatable" class="basic-datatables table table-bordered dt-responsive" style="border-collapse: collapse; border-spacing: 0; width: 100%;">
                    <thead>
                        <tr>
                            <th>Cluster ID</th>
                            <th>Jumlah Tweet</th>
                            <th>Purity</th>
                            <th>Persentase</th> <!-- Kolom tambahan untuk persentase -->
                            <th>Quality</th>
                            <th>Jumlah Dokumen</th> <!-- Kolom tambahan untuk jumlah dokumen -->
                        </tr>
                    </thead>
                    <tbody>
                    <?php
                         // Menampilkan hasil purity per cluster
                            if (isset($result_purity_cluster) && mysqli_num_rows($result_purity_cluster) > 0) {
                                while ($row = mysqli_fetch_assoc($result_purity_cluster)) {
                                    $persentase = $row['purity'] * 100; // Mengonversi purity ke persentase
                                    $deskripsi = ($persentase > 50) ? 'Baik' : 'Kurang Baik'; // Menentukan deskripsi berdasarkan nilai purity
                                    ?>
                                    <tr>
                                        <td><?= $row['cluster_id']; ?></td>
                                        <td><?= $row['jumlah_tweet']; ?></td>
                                        <td><?= $row['purity']; ?></td>
                                        <td><?= number_format($persentase, 2) . '%'; ?></td> <!-- Menampilkan persentase -->
                                        <td><?= $row['quality']; ?></td>
                                        <td><?= $row['jumlah_tweet']; ?></td> <!-- Menampilkan jumlah dokumen -->
                                    </tr>
                                    <?php
                                }
                            } else {
                                echo "<tr><td colspan='6' class='text-center'>Tidak ada data</td></tr>";
                            }
                            ?>
                    </tbody>
                </table>

                <!-- Menampilkan total purity dan rata-rata purity -->
                <h5 class="card-title mt-4">Purity Per-dokumen</h5>
                <table class="table table-bordered dt-responsive" style="border-collapse: collapse; border-spacing: 0; width: 100%;">
                    <thead>
                        <tr>
                            <th>Nilai Purity (100 Dokumen)</th>
                            <th>Nilai Purity (200 Dokumen)</th>
                            <th>Nilai Purity (300 Dokumen)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><?= isset($overall_purity_all) ? number_format($overall_purity_all * 100, 2) . '%' : 'N/A'; ?></td> <!-- Nilai Purity untuk semua dokumen -->
                            <td><?= isset($overall_purity_200_random) ? number_format($overall_purity_200_random * 100, 2) . '%' : 'N/A'; ?></td> <!-- Nilai Purity untuk 200 dokumen berurutan -->
                            <td><?= isset($overall_purity_100_random) ? number_format($overall_purity_100_random * 100, 2) . '%' : 'N/A'; ?></td> <!-- Nilai Purity untuk 100 dokumen cluster 1-10 -->
                        </tr>
                    </tbody>
                </table>

                <!-- Menambahkan statistik purity baik dan buruk ke dalam tabel -->
                <h5 class="card-title mt-4">Statistik Purity</h5>
                <table class="table table-bordered dt-responsive" style="border-collapse: collapse; border-spacing: 0; width: 100%;">
                    <thead>
                        <tr>
                            <th>Kategori</th>
                            <th>Jumlah Kluster</th>
                            <th>Daftar Kluster</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Purity Baik (>50%)</td>
                            <td><?= count($clusters_baik); ?></td>
                            <td><?= implode(', ', $clusters_baik); ?></td>
                        </tr>
                        <tr>
                            <td>Purity Buruk (<=50%)</td>
                            <td><?= count($clusters_buruk); ?></td>
                            <td><?= implode(', ', $clusters_buruk); ?></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<?php
$title = "pengujian";
$page_title = "pengujian";
$content = ob_get_clean();
include 'layout.php';
?>
