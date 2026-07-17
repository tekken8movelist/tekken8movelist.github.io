# -*- coding: utf-8 -*-
"""Regression contract for the Marshall Law movelist deliverable."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import pipeline


ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "马歇尔·洛_铁拳8_出招表.html"
WAVU = ROOT / "tools" / "wavu_law.txt"


class LawPageContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_pipeline_has_law_configuration(self) -> None:
        cfg = pipeline.CONFIG["law"]
        expected = {
            "file": PAGE.name,
            "wavu": WAVU.name,
            "acc": "#ffe07a",
            "acc_ink": "#6e5200",
            "states": [
                "热能中龙构中",
                "倒地仰面时",
                "自动格挡拳技",
                "龙构中",
                "背身时",
            ] + pipeline.COMMON_STATES,
            "prefix": dict(
                pipeline.COMMON_PREFIX,
                **{
                    "热能中龙构中": "H.DSS.",
                    "龙构中": "DSS.",
                    "背身时": "BT.",
                    "蹲伏中": "hFC.",
                    "起身中": "ws",
                    "横移中": "ss",
                    "倒地仰面时": "(While_down,_facing_up).",
                },
            ),
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(cfg[key], value)
        frames, lower = pipeline.load_wavu(WAVU)
        self.assertEqual(
            pipeline.lookup("背墙时 b,b,u/b", cfg, frames, lower),
            "i29~33",
        )

    def test_wavu_snapshot_is_complete_and_well_formed(self) -> None:
        lines = [line for line in WAVU.read_text(encoding="utf-8").splitlines() if line]
        self.assertGreaterEqual(len(lines), 160)
        commands = []
        for line in lines:
            command, startup = line.split("|", 1)
            self.assertTrue(command)
            self.assertRegex(startup, r"^(?:i\d.*)?$")
            commands.append(command)
        self.assertEqual(len(commands), len(set(commands)))
        snapshot = "\n".join(lines)
        for canonical in (
            "Left_Throw|i12~14",
            "Right_Throw|i12~14",
            "Back_Throw|i12~14",
            "(Back_to_wall).b,b,ub|i29~33",
            "(While_down,_facing_up).1+2+3+4|",
        ):
            self.assertIn(canonical, snapshot)
        self.assertNotIn("Left throw|", snapshot)
        self.assertNotIn("(Back to wall).", snapshot)

    def test_lookup_skips_empty_prefix_candidate(self) -> None:
        cfg = pipeline.CONFIG["law"]
        frames = {"ub+3": "", "ub+3,4": "i15", "d+1+2": ""}
        lower = {command.lower(): startup for command, startup in frames.items()}

        self.assertEqual(pipeline.lookup("u/b+3,4", cfg, frames, lower), "i15")
        self.assertEqual(pipeline.lookup("d+1+2", cfg, frames, lower), "—")
        self.assertIsNone(pipeline.lookup("f+1", cfg, frames, lower))

    def test_rendered_startups_match_wavu_lookup(self) -> None:
        cfg = pipeline.CONFIG["law"]
        frames, lower = pipeline.load_wavu(WAVU)
        movelist = self.html.split('<section class="tipsPage">', 1)[0]
        rendered = re.findall(
            r'<td class="name">.*?<span class="cmd-txt">([^<]*)</span>'
            r'</td><td class="fr">([^<]*)</td>',
            movelist,
            re.S,
        )
        self.assertEqual(len(rendered), 170)
        covered = 0
        for command, startup in rendered:
            expected = pipeline.lookup(command, cfg, frames, lower)
            if expected is None:
                continue
            covered += 1
            with self.subTest(command=command):
                self.assertEqual(startup, expected)
        self.assertGreaterEqual(covered, 169)

    def test_page_matches_existing_interactive_design_contract(self) -> None:
        html = self.html
        self.assertIn("<title>马歇尔·洛 · 铁拳8 出招表</title>", html)
        self.assertIn('id="tk-notation"', html)
        self.assertIn('id="thd"', html)
        self.assertIn('id="thl"', html)
        self.assertIn('id="ng"', html)
        self.assertIn('id="nn"', html)
        self.assertIn('id="nt"', html)
        self.assertIn("localStorage.setItem(KEY,m)", html)
        self.assertIn("@media (max-width: 760px)", html)
        self.assertIn("@media screen { body { zoom: 1.25; } }", html)
        self.assertIn("Law_movelist", html)
        self.assertIn("Law_combos", html)
        self.assertIn("TekkenDocs", html)
        self.assertNotIn("</span>、<span", html)
        self.assertNotIn("<th>发生</th><th>判定</th><th>伤害</th>", html)
        self.assertIn("<th>发生</th><th>伤害</th><th>判定</th>", html)
        self.assertNotRegex(
            html,
            r'<td class="fr">.*?</td><td class="rng">.*?</td><td class="dmg">',
        )
        self.assertIn("龙构=龙构架势(DSS)", html)
        self.assertIn("背身=背身状态(BT)", html)
        self.assertIn("路线 (T!=回旋 · ~F=按住前 · →=下一招)", html)

        self.assertGreaterEqual(html.count('<td class="cmd">'), 165)
        self.assertGreaterEqual(html.count('class="cmd-gfx"'), 160)
        self.assertGreaterEqual(html.count('class="cmd-txt"'), 160)
        self.assertGreaterEqual(html.count('class="fr">i'), 145)
        self.assertEqual(html.count("<table"), html.count("</table>"))
        self.assertEqual(html.count("<section"), html.count("</section>"))

    def test_move_names_are_chinese(self) -> None:
        html = self.html
        names = re.findall(r'<td class="name">([^<]+)</td>', html)
        self.assertGreaterEqual(len(names), 150)
        untranslated = [name for name in names if re.search(r"[A-Za-z]", name)]
        self.assertEqual(untranslated, [])

    def test_primary_lists_are_balanced_without_duplicate_groups(self) -> None:
        html = self.html
        throws_start = html.index("<h2>投技")
        attacks_start = html.index("<h2>打击技")
        throws = html[throws_start:html.index("</section>", throws_start)]
        attacks = html[attacks_start:html.index("</section>", attacks_start)]

        self.assertIn('class="cols2 balanced-movelists"', throws)
        self.assertIn('class="cols2 balanced-movelists"', attacks)
        self.assertIn('class="movelist balanced-list throws-list"', throws)
        self.assertIn('class="movelist balanced-list attacks-list"', attacks)
        self.assertNotIn('class="grp"', throws)
        self.assertNotIn('class="grp"', attacks)

        duplicate_labels = (
            "投技", "基础技", "前向技", "前下技", "下段技", "后下技",
            "后向技", "跳跃技", "移动输入", "蹲伏技", "起身技",
        )
        for label in duplicate_labels:
            self.assertNotIn(f'<th colspan="5">{label}</th>', throws + attacks)

        for chunk, expected_moves, expected_rows, expected_cells in (
            (throws, 9, (5, 4), 6),
            (attacks, 116, (58, 58), 5),
        ):
            self.assertEqual(chunk.count('<td class="name">'), expected_moves)
            bodies = re.findall(r"<tbody>(.*?)</tbody>", chunk, re.S)
            self.assertEqual(len(bodies), 2)
            rows = [re.findall(r"<tr>(.*?)</tr>", body, re.S) for body in bodies]
            self.assertEqual(tuple(map(len, rows)), expected_rows)
            self.assertTrue(
                all(row.count("<td") == expected_cells for side in rows for row in side)
            )

        self.assertIn(".balanced-movelists{", html)
        self.assertIn("gap:0 24px", html)
        self.assertIn(".balanced-list tbody tr{height:", html)

    def test_p0_rows_and_throw_schema(self) -> None:
        html = self.html

        shoryu = re.search(r'<tr><td class="name">升龙炮</td>.*?</tr>', html, re.S)
        self.assertIsNotNone(shoryu)
        self.assertIn('<span class="tk-dir uf"></span>', shoryu.group())
        self.assertIn('<span class="tk-n">N</span>', shoryu.group())
        self.assertIn('<span class="cmd-txt">u/f, N, 4</span>', shoryu.group())
        self.assertIn('<td class="fr">i19</td>', shoryu.group())

        backflip = re.search(r'<tr><td class="name">空翻虚招</td>.*?</tr>', html, re.S)
        self.assertIsNotNone(backflip)
        self.assertIn('<td class="fr">i15</td>', backflip.group())

        cloud_gate = next(
            (
                row
                for row in re.findall(r"<tr>.*?</tr>", html, re.S)
                if '<td class="name">云门</td>' in row
                and '<span class="cmd-txt">1+2+3+4,1+2*,2</span>' in row
            ),
            None,
        )
        self.assertIsNotNone(cloud_gate)
        self.assertIn('<td class="fr">i14</td>', cloud_gate)
        self.assertEqual(html.count('<td class="fr">—</td>'), 9)

        throws_start = html.index("<h2>投技")
        throws = html[throws_start:html.index("</section>", throws_start)]
        header = (
            "<tr><th>招式</th><th>指令</th><th>发生</th>"
            "<th>方向</th><th>伤害</th><th>挣脱</th></tr>"
        )
        self.assertEqual(throws.count(header), 2)
        expected = {
            "龙火投": ("正面", "1或2"),
            "跃蛙投": ("正面", "1或2"),
            "夹头踢": ("左侧", "1"),
            "破裆摔": ("右侧", "2"),
            "龙噬": ("背后", "—"),
            "冲刺抱摔": ("正面", "1"),
            "夹头拳": ("正面", "1+2"),
            "夹头落": ("正面", "1+2"),
            "抬膝摔": ("正面", "1+2"),
        }
        for name, (direction, escape) in expected.items():
            row = re.search(
                rf'<tr><td class="name">{name}</td>(.*?)</tr>', throws, re.S
            )
            self.assertIsNotNone(row, name)
            cells = re.findall(r"<td\b.*?</td>", row.group(), re.S)
            self.assertEqual(len(cells), 6, name)
            self.assertEqual(re.sub(r"<.*?>", "", cells[3]), direction, name)
            self.assertEqual(re.sub(r"<.*?>", "", cells[5]), escape, name)

    def test_synced_list_rows_do_not_wrap(self) -> None:
        html = self.html
        self.assertEqual(html.count('class="lt synced-lists"'), 2)
        self.assertIn(".synced-lists .movelist tr:not(.grp){height:38px}", html)
        self.assertIn(".synced-lists td.cmd .tk-in{flex-wrap:nowrap}", html)
        self.assertIn(".synced-lists .movelist th:nth-child(4){width:18%}", html)
        self.assertIn(".synced-lists .movelist td.dmg{font-size:9px}", html)

    def test_secondary_movelist_groups_contain_moves(self) -> None:
        html = self.html
        labels = (
            "龙构",
            "背身",
            "横移",
            "其他",
            "热能专用与强化",
            "十连技",
        )
        for label in labels:
            marker = f'<tr class="grp"><th colspan="5">{label}</th></tr>'
            start = html.index(marker) + len(marker)
            next_group = html.find('<tr class="grp">', start)
            table_end = html.find("</table>", start)
            end = min(position for position in (next_group, table_end) if position != -1)
            self.assertIn('<td class="name">', html[start:end], label)

        heat_marker = '<tr class="grp"><th colspan="5">热能专用与强化</th></tr>'
        heat_start = html.index(heat_marker) + len(heat_marker)
        heat_end = html.index("</table>", heat_start)
        self.assertLessEqual(html[heat_start:heat_end].count('<td class="name">'), 15)

        ten_hit_start = html.index('<td class="name">十连技</td>')
        ten_hit_end = html.index("</tr>", ten_hit_start)
        self.assertEqual(html[ten_hit_start:ten_hit_end].count('class="tk-b"'), 10)


if __name__ == "__main__":
    unittest.main()
