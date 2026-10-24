import io, json, os, tempfile, unittest
from contextlib import redirect_stdout
from export_to_redis import load_entries, main

SAMPLE = """<config>
  <subdomains>
    <subdomain>http://a.example.com</subdomain>
    <subdomain>https://b.example.com</subdomain>
  </subdomains>
  <cookies>
    <cookie name="dlp-avast" host="amazon">mmm_amz_dlp_777_ppc_m</cookie>
    <cookie name="dlp-avg" host="filehippo">Mmm_fhp_dlp_779_ppc_m</cookie>
  </cookies>
</config>"""

# stand-in for Redis, just keeps dictionary in memory
class FakeRedis:
    def __init__(self):
        self.data = {}

    def mset(self, mapping):
        self.data.update(mapping)

# write text to temp file and return path
def make_xml(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False)
    f.write(text)
    f.close()
    return f.name


class LoadEntriesTests(unittest.TestCase):
    def test_subdomains_are_a_json_list(self):
        entries = load_entries(make_xml(SAMPLE))
        self.assertEqual(json.loads(entries["subdomains"]), ["http://a.example.com", "https://b.example.com"])

    def test_cookie_keys_and_values(self):
        entries = load_entries(make_xml(SAMPLE))
        self.assertEqual(entries["cookie:dlp-avast:amazon"], "mmm_amz_dlp_777_ppc_m")
        self.assertEqual(entries["cookie:dlp-avg:filehippo"], "Mmm_fhp_dlp_779_ppc_m")

    def test_real_config_file(self):
        path = os.path.join(os.path.dirname(__file__), "config.xml")
        entries = load_entries(path)
        self.assertEqual(len(entries), 47)  # 1 subdomains key and 46 cookies


class MainTests(unittest.TestCase):
    def test_saves_everything_to_redis(self):
        fake = FakeRedis()
        self.assertEqual(main([make_xml(SAMPLE)], fake), 0)
        self.assertEqual(len(fake.data), 3)

    def test_verbose_prints_all_keys(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main(["-v", make_xml(SAMPLE)], FakeRedis())
        self.assertIn("cookie:dlp-avast:amazon = mmm_amz_dlp_777_ppc_m", out.getvalue())
        self.assertIn("subdomains = ", out.getvalue())

    def test_silent_without_v(self):
        out = io.StringIO()
        with redirect_stdout(out):
            main([make_xml(SAMPLE)], FakeRedis())
        self.assertEqual(out.getvalue(), "")

    def test_missing_file_gives_error_code(self):
        fake = FakeRedis()
        self.assertEqual(main(["/no/such/file.xml"], fake), 1)
        self.assertEqual(fake.data, {})

    def test_no_path_gives_usage_code(self):
        self.assertEqual(main([], FakeRedis()), 2)


if __name__ == "__main__":
    unittest.main()
