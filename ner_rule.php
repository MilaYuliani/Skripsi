<?php
session_start();
ob_start();

if (isset($_POST['proses'])) {
    // Memanggil skrip Python untuk pemrosesan NER
    $output = passthru("python ner_rule.py");

    // Koneksi ke database MySQL
    $conn = mysqli_connect("localhost", "root", "", "databanjir");

    // Memanggil hasil dari tabel ner setelah proses Python
    $sql_ner = "SELECT * FROM ner";
    $result_ner = mysqli_query($conn, $sql_ner);

    // Simpan hasil query ke sesi
    $_SESSION['result_ner'] = [];
    while ($row = mysqli_fetch_assoc($result_ner)) {
        $_SESSION['result_ner'][] = $row;
    }
}

if (isset($_POST['hapus'])) {
    // Koneksi ke database MySQL
    $conn = mysqli_connect("localhost", "root", "", "databanjir");

    // Menghapus semua data dari tabel ner
    $sql_delete = "DELETE FROM ner";
    mysqli_query($conn, $sql_delete);

    // Mengatur ulang auto-increment
    $sql_reset_ai = "ALTER TABLE ner AUTO_INCREMENT = 1";
    mysqli_query($conn, $sql_reset_ai);

    // Hapus data dari sesi
    unset($_SESSION['result_ner']);
}
?>

<div class="card-header">
    <form method="post">
        <button type="submit" class="btn btn-primary" name="proses">Proses</button>
        <button type="submit" class="btn btn-danger" name="hapus">Hapus</button>
    </form>
</div>
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-body">
                <div style="display: flex;">
                    <!-- Tabel NER Lengkap -->
                    <div style="flex: 1; margin-right: 20px;">
                        <h4>Proses Tokenisasi dan Pemilihan Fitur</h4>
                        <table id="datatable-full" class="basic-datatables table table-bordered dt-responsive"
                            style="border-collapse: collapse; border-spacing: 0; width: 100%;">
                            <thead>
                                <tr>
                                    <th>id</th>
                                    <th>Token String</th>
                                    <th>Token Kind</th>
                                    <th>Contextual Features</th>
                                    <th>Morphological Features</th>
                                    <th>Part of Speech Features</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php
                                // Menampilkan hasil preprocessing dari sesi
                                if (isset($_SESSION['result_ner'])) {
                                    foreach ($_SESSION['result_ner'] as $row) {
                                        ?>
                                        <tr>
                                            <td class="col-1">
                                                <?= $row['id']; ?>
                                            </td>
                                            <td class="col-2">
                                                <?= $row['token_string']; ?>
                                            </td>
                                            <td class="col-2">
                                                <?= $row['token_kind']; ?>
                                            </td>
                                            <td class="col-2">
                                                <?= $row['contextual_features']; ?>
                                            </td>
                                            <td class="col-2">
                                                <?= $row['morphological_features']; ?>
                                            </td>
                                            <td class="col-2">
                                                <?= $row['part_of_speech_features']; ?>
                                            </td>
                                        </tr>
                                        <?php
                                    }
                                }
                                ?>
                            </tbody>
                        </table>
                    </div>

                    <!-- Tabel Token dan Entity Type -->
                    <div style="flex: 1;">
                        <h4>Hasil NER</h4>
                        <table id="datatable-simple" class="basic-datatables table table-bordered dt-responsive"
                            style="border-collapse: collapse; border-spacing: 0; width: 100%;">
                            <thead>
                                <tr>
                                    <th>Token String</th>
                                    <th>Entity Type</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php
                                // Menampilkan hasil preprocessing dari sesi
                                if (isset($_SESSION['result_ner'])) {
                                    foreach ($_SESSION['result_ner'] as $row) {
                                        ?>
                                        <tr>
                                            <td class="col-6">
                                                <?= $row['token_string']; ?>
                                            </td>
                                            <td class="col-6">
                                                <?= $row['entity_type']; ?>
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
    </div>
</div>

<?php
$title = "NER Rule-Based";
$page_title = "NER Rule-Based";
$content = ob_get_clean();
include 'layout.php';
?>