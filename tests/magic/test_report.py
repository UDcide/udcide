from udcide.report import Report
import pytest

@pytest.fixture(scope='class')
def report():
    with open('test_report.json', 'w') as report:
        report.write("""
{"md5": "f7c6a49ddb8e2b614c9f7957e52d68e2","apk_filename": "Ahmyth.s.apk","size_bytes":
269787,"threat_level": "Moderate Risk","total_score": 153,"crimes": [{"crime":
"Initialize bitmap object and compress data (e.g. JPEG) into bitmap object","score": 1,"weight": 1.0,
"confidence": "100%","permissions": [],"native_api": [{"class": "Landroid/graphics/BitmapFactory;",
"method": "decodeByteArray"},{"class": "Landroid/graphics/Bitmap;","method": "compress"}],
"combination": [{"class": "Landroid/graphics/BitmapFactory;","method": "decodeByteArray",
"descriptor": "([B I I)Landroid/graphics/Bitmap;"},{"class": "Landroid/graphics/Bitmap;",
"method": "compress","descriptor": "(Landroid/graphics/Bitmap$CompressFormat; I Ljava/io/OutputStream;)Z"
}],"sequence": [{"Lahmyth/mine/king/ahmyth/CameraManager; sendPhoto ([B)V": {"first": ["invoke-static",
"v9","v4","v5","Landroid/graphics/BitmapFactory;->decodeByteArray([B I I)Landroid/graphics/Bitmap;"],
"first_hex": "71 30 61 00 49 05","second": ["invoke-virtual","v0","v4","v5","v1",
"Landroid/graphics/Bitmap;->compress(Landroid/graphics/Bitmap$CompressFormat; I Ljava/io/OutputStream;)Z"
],"second_hex": "6e 40 60 00 40 15"}}]}]}
""")

    return 'test_report.json'

class Test_report:
    @staticmethod
    def test_parse_report(report):
        report = Report.parse_report(report)

        assert report.md5 == 'f7c6a49ddb8e2b614c9f7957e52d68e2'
        assert report.apk_filename == 'Ahmyth.s.apk'
        assert len(report.crimes) == 1

        crime = report.crimes[0]
        assert crime.description == "Initialize bitmap object and compress data (e.g. JPEG) into bitmap object"
        assert set(crime.native_apis) == {
            "Landroid/graphics/BitmapFactory;->decodeByteArray([B I I)Landroid/graphics/Bitmap;",
            "Landroid/graphics/Bitmap;->compress(Landroid/graphics/Bitmap$CompressFormat; I Ljava/io/OutputStream;)Z"
        }
        assert set(crime.sequences) == {
            "Lahmyth/mine/king/ahmyth/CameraManager; sendPhoto ([B)V"
        }
