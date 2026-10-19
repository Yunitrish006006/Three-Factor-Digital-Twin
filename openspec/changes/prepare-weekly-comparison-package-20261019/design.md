# Design

WPK-901 reads complete frozen evidence and emits a new audit receipt, never writes earlier artifacts. WPK-902 creates one Chinese Markdown manuscript with computed tables inserted by a builder; both HTML and PDF derive from that source. WPK-903 creates an offline weekly briefing and talk linking the earlier LQR guide and original paper, with current task status. Reporting is neutral and separate from the adopted thesis artifacts.

Use native installed BiauKai for Chinese and Times New Roman for Latin/numbers. ReportLab makes the candidate PDF; no Office dependency. Preserve the original template separately with source URL/hash. Use a supplied Playwright dependency path and isolated local Chrome when no in-app browser tool is available. Observe final output before declaring visual completion.
