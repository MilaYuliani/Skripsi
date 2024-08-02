<?php
ob_start();
session_start();
include "koneksi.php";

// Fungsi untuk menghapus semua data dari tabel
if (isset($_POST['delete_all'])) {
    $query = "DELETE FROM datacraw";
    if ($conn->query($query) === TRUE) {
        // Mengatur ulang AUTO_INCREMENT
        $reset_ai_query = "ALTER TABLE datacraw AUTO_INCREMENT = 1";
        if ($conn->query($reset_ai_query) === TRUE) {
            $_SESSION['message'] = "";
        } else {
            $_SESSION['message'] = "Data berhasil dihapus, tetapi gagal mengatur ulang AUTO_INCREMENT.";
        }
    } else {
        $_SESSION['message'] = "Gagal menghapus semua data.";
    }
    header("Location: index.php");
    exit();
}
?>
<div class="container">
    <div class="row">
        <div class="col-md-12 mt-4">
            <?php
            if (isset($_SESSION['message'])) {
                echo "<h4>".$_SESSION['message']."</h4>";
                unset($_SESSION['message']);
            }
            ?>
            <div class="card">
                <div class="card-body">
                <form action="proses_craw.php" method="post" enctype="multipart/form-data" style="display:inline;">
                    <div class="form-group">
                        <label for="fileToUpload">Pilih file Excel:</label>
                        <input type="file" class="form-control-file" id="excel_file" name="excel_file" accept=".xls, .xlsx, .csv">
                    </div>
                    <br>
                    <button type="submit" class="btn btn-primary" onclick="showAlert()">Import</button>
                </form>
                <form action="crawling.php" method="post" style="display:inline;">
                    <input type="hidden" name="delete_all" value="true">
                    <button type="submit" class="btn btn-danger" onclick="return confirm('Apakah Anda yakin ingin menghapus semua data?')">Hapus</button>
                </form>
                </div>
            </div>
            <div class="card-header text-right"></div>
        </div>
    </div>
</div>
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <table id="datatable" class="basic-datatables table table-bordered dt-responsive" style="border-collapse: collapse; border-spacing: 0; width: 100%;">
                    <thead>
                        <tr>
                            <th>tweet_id</th>
                            <th>created_at</th>
                            <th>username</th>
                            <th>full_text</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php
                        $query = mysqli_query($conn, "SELECT * FROM datacraw");
                        while ($row = mysqli_fetch_assoc($query)) {
                        ?>
                            <tr>
                                <td class="col-1"><?= $row['tweet_id']; ?></td>
                                <td class="col-1"><?= $row['created_at']; ?></td>
                                <td class="col-1"><?= $row['username']; ?></td>
                                <td class="col-8"><?= $row['full_text']; ?></td>
                            </tr>
                        <?php
                        }
                        ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<?php
$title = "Crawling";
$page_title = "Data Hasil Crawling";
$content = ob_get_clean();
include 'layout.php';
?>
