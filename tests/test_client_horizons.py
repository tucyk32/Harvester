import os, pytest
from client_horizons import fetch_ephem

@pytest.mark.skipif(os.environ.get("RUN_HORIZONS_TEST","0") != "1", reason="Test online (ustaw RUN_HORIZONS_TEST=1)")
def test_fetch_small_range():
    # J2000 ± 1 dzień
    df = fetch_ephem('Sun', 2451544.5, 2451546.5, step='6h', site='500', chunk_days=2)
    assert not df.empty
    for col in ('jd_utc','jd_tt','delta_t_sec','target','site'):
        assert col in df.columns