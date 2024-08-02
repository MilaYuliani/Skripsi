<?php
ob_start();
session_start();
set_time_limit(300);

include "koneksi.php";

if (isset($_POST['proses'])) {
    // Memanggil skrip Python untuk preprocessing dan perhitungan
    $output = shell_exec("python test_mc.py");

    // Memastikan skrip Python telah berjalan dengan benar
    if (strpos($output, "Error") !== false) {
        echo "Terjadi kesalahan dalam menjalankan skrip Python.";
    } else {
        echo "";
    }

    // Menyimpan status pemrosesan ke sesi
    $_SESSION['proses_selesai'] = true;
}

// Proses penyimpanan label yang diinput manual
if (isset($_POST['save_labels'])) {
    foreach ($_POST['labels'] as $id => $label) {
        $sql_update = "UPDATE clusters SET label = '".mysqli_real_escape_string($conn, $label)."' WHERE id = '".mysqli_real_escape_string($conn, $id)."'";
        mysqli_query($conn, $sql_update) or die(mysqli_error($conn));
    }
    // Reload halaman untuk memperbarui tampilan tabel
    header("Location: ".$_SERVER['PHP_SELF']);
    exit;
}

// Proses penghapusan semua label
if (isset($_POST['delete_all_labels'])) {
    $sql_delete_all = "UPDATE clusters SET label = ''";
    mysqli_query($conn, $sql_delete_all) or die(mysqli_error($conn));
    // Reload halaman untuk memperbarui tampilan tabel
    header("Location: ".$_SERVER['PHP_SELF']);
    exit;
}

// Mengambil hasil clustering dan Jaccard Similarity dari database
$result_clusters = null;
$result_jaccard = null;

if (isset($_SESSION['proses_selesai']) && $_SESSION['proses_selesai']) {
    $sql_clusters = "SELECT * FROM clusters ORDER BY cluster_id";
    $result_clusters = mysqli_query($conn, $sql_clusters);

    $sql_jaccard = "SELECT * FROM model LIMIT 3000";
    $result_jaccard = mysqli_query($conn, $sql_jaccard);
}
?>

<!-- Tambahkan gaya CSS untuk dropdown biru -->
<style>
.blue-dropdown select {
    background-color: #007bff; /* Warna biru */
    color: white;
}
.blue-dropdown option {
    background-color: white;
    color: black;
}
</style>

<div class="card-header">
    <div class="d-flex justify-content-between">
        <form method="post">
            <button type="submit" class="btn btn-primary" name="proses">Proses</button>
        </form>
    </div>
</div>

<div class="row">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Hasil Jaccard Similarity</h5>
                <table id="datatable" class="basic-datatables table table-bordered dt-responsive" style="border-collapse: collapse; border-spacing: 0; width: 100%;">
                    <thead>
                        <tr>
                            <th>perbandingan</th>
                            <th>First Pair</th>
                            <th>Second Pair</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                    <?php
                    // Menampilkan hasil Jaccard Similarity
                    if ($result_jaccard) {
                        while ($row = mysqli_fetch_assoc($result_jaccard)) {
                            ?>
                            <tr>
                                <td class="col-1"><?= htmlspecialchars($row['tweet_id']); ?></td>
                                <td><?= htmlspecialchars($row['first_pair_jaccard']); ?></td>
                                <td><?= htmlspecialchars($row['second_pair_jaccard']); ?></td>
                                <td><?= htmlspecialchars($row['key_score_jaccard']); ?></td>
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

<div class="row mt-3">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Hasil Clustering</h5>
                <form method="post">
                    <table id="datatable-clusters" class="table table-bordered dt-responsive nowrap" style="width:100%">
                    <div class="button-container text-left mt-3">
                        <button type="submit" class="btn btn-success" name="save_labels">Update</button>
                        <button type="submit" class="btn btn-danger" name="delete_all_labels">Delete</button>
                    </div><br>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Cluster ID</th>
                                <th>Text</th>
                                <th>Label</th>
                            </tr>
                        </thead>
                        <tbody>
                        <?php
                        // Menampilkan hasil clustering
                        if ($result_clusters) {
                            while ($row = mysqli_fetch_assoc($result_clusters)) {
                                ?>
                                <tr>
                                    <td><?= htmlspecialchars($row['id']); ?></td>
                                    <td><?= htmlspecialchars($row['cluster_id']); ?></td>
                                    <td><?= htmlspecialchars($row['text']); ?></td>
                                    <td class="blue-dropdown">
                                        <select name="labels[<?= htmlspecialchars($row['id']); ?>]" class="form-control">
                                            <option value="">Pilih Label</option>
                                            <option value="banjir" <?= $row['label'] == 'banjir' ? 'selected' : ''; ?>>Banjir</option>
                                            <option value="banjir bandang" <?= $row['label'] == 'banjir bandang' ? 'selected' : ''; ?>>Banjir Bandang</option>
                                            <option value="banjir lahar" <?= $row['label'] == 'banjir lahar' ? 'selected' : ''; ?>>Banjir lahar</option>
                                            <option value="banjir rob" <?= $row['label'] == 'banjir rob' ? 'selected' : ''; ?>>Banjir Rob</option>
                                            <option value="banjir sungai" <?= $row['label'] == 'banjir sungai' ? 'selected' : ''; ?>>Banjir Sungai</option>
                                            <option value="banjir tanah longsor" <?= $row['label'] == 'banjir tanah longsor' ? 'selected' : ''; ?>>Banjir & Tanah longsor</option>
                                            <option value="tanah longsor" <?= $row['label'] == 'tanah longsor' ? 'selected' : ''; ?>>Tanah Longsor</option>
                                            <option value="gempa bumi" <?= $row['label'] == 'gempa bumi' ? 'selected' : ''; ?>>Gempa Bumi</option>
                                        </select>
                                    </td>
                                </tr>
                                <?php
                            }
                        }
                        ?>
                        </tbody>
                    </table>
                </form>
            </div>
        </div>
    </div>
</div>

<?php
$title = "clustering";
$page_title = "clustering";
$content = ob_get_clean();
include 'layout.php';
?>
