import vl_convert as vlc

vl_spec = r"""
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"url": "data/movies.json"},
  "mark": "circle",
  "encoding": {
    "x": {
      "bin": {"maxbins": 10},
      "field": "IMDB Rating"
    },
    "y": {
      "bin": {"maxbins": 10},
      "field": "Rotten Tomatoes Rating"
    },
    "size": {"aggregate": "count"}
  }
}
"""

png_data = vlc.vegalite_to_png(vl_spec=vl_spec, scale=2)
with open("chart.png", "wb") as f:
    f.write(png_data)