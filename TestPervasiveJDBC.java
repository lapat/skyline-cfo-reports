import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;

public class TestPervasiveJDBC {
    public static void main(String[] args) {
        String host = (args.length >= 1) ? args[0] : "172.17.21.167";
        String dbName = (args.length >= 2) ? args[1] : "DEMODATA";
        String user = (args.length >= 3) ? args[2] : "Master";
        String password = (args.length >= 4) ? args[3] : "";

        String url = "jdbc:pervasive://" + host + ":1583/" + dbName;
        System.out.println("Connecting to: " + url);

        try {
            Class.forName("com.pervasive.jdbc.v2.Driver");
            Connection conn = DriverManager.getConnection(url, user, password);
            System.out.println("✅ SUCCESS: Connected to Pervasive Engine!");

            System.out.println("\nRegistered Databases / Catalogs on this Server:");
            ResultSet catalogs = conn.getMetaData().getCatalogs();
            while (catalogs.next()) {
                System.out.println(" - " + catalogs.getString(1));
            }
            catalogs.close();

            conn.close();
        } catch (Exception e) {
            System.err.println("❌ ERROR: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
