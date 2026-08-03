import unittest
import xml.etree.ElementTree as ET

from scripts import build_architecture_diagrams


class ArchitectureDiagramTests(unittest.TestCase):
    def test_research_logic_architecture_renders_valid_svg(self):
        svg = build_architecture_diagrams.svg_research_logic_architecture()

        ET.fromstring(svg)
        self.assertIn("研究整體邏輯架構", svg)
        self.assertIn("RQ1 空間場估計", svg)
        self.assertIn("E1-E3 / E6 / E7", svg)
        self.assertIn("future intervention protocol", svg)
        self.assertIn("不作 headline novelty", svg)

    def test_system_abstraction_tree_renders_valid_svg(self):
        svg = build_architecture_diagrams.svg_overall_architecture()

        ET.fromstring(svg)
        self.assertIn("系統整體抽象樹狀架構", svg)
        self.assertIn("情境與觀測層", svg)
        self.assertIn("估測與學習層", svg)
        self.assertIn("MCP + Gemma bridge", svg)

    def test_research_logic_architecture_en_renders_valid_svg(self):
        svg = build_architecture_diagrams.svg_research_logic_architecture_en()

        ET.fromstring(svg)
        self.assertIn("Overall Research Logic Architecture", svg)
        self.assertIn("RQ1 Field estimation", svg)
        self.assertIn("Not causal identification", svg)
        self.assertNotIn("研究整體邏輯架構", svg)


if __name__ == "__main__":
    unittest.main()
