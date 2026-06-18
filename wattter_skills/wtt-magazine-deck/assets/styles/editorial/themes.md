# 主题色预设（Themes）

5 套精心调配的主题色板,保证"电子杂志 × 电子墨水"的美学不垮。预设优先；如果用户给了明确品牌/主题色，可以生成 deck 专属 `theme.css`，但不要在 HTML 里散写颜色。

**主题决定整个画面风格**：每套主题定义 `--ink`/`--paper`/`--accent`/`--accent-2` 等颜色变量,WebGL 流体背景（hero 页 shader）会读取这些变量。换主题时文字色 + 底色遮罩 + 流体背景配色一起变——不是只换字色。

---

## 使用方法

1. 问用户选哪套(或基于内容推荐一套，见文末「内容 → 主题推荐表」)
2. 预设主题：复制全部预设主题到 `css/`，并让 `theme-link` 指向具体主题文件，例如 `css/ink-classic.css`：
   ```bash
   cp <SKILL_ROOT>/assets/styles/editorial/themes/*.css 项目/XXX/deck/css/
   ```
3. 明确品牌/主题色使用：
   ```bash
   node <SKILL_ROOT>/scripts/make-custom-theme.mjs editorial "#RRGGBB" "$DIR/css/theme.css" --name="brand-name"
   ```
4. `index.html` 中的 `<link id="theme-link">` 会自动加载。要启用 T 键切换预设主题，复制全部预设主题到 `css/`，并让 `theme-link` 指向具体主题文件，例如 `css/ink-classic.css`。
5. 微动/沉浸/静态模式下 T 键可实时切换 5 套预设主题（切完后流体背景平滑变色）。如果 `theme-link` 指向一次性 `css/theme.css`，T 键会保持锁定，避免覆盖用户自定义主题。

### 主题文件对应

| # | 主题 | 文件 | 适合 | 气质 |
|---|------|------|------|------|
| 1 | 🖋 墨水经典 | `ink-classic.css` | 通用 / 商业发布 / 默认 | 墨黑+暖米白，冷灰蓝点缀 |
| 2 | 🌊 靛蓝瓷 | `indigo-porcelain.css` | 科技 / 研究 / 数据 / 理性叙事 | 深靛蓝+冷瓷白，蓝青花瓷感 |
| 3 | 🌿 森林墨 | `forest-ink.css` | 自然 / 可持续 / 文化 / 非虚构 | 墨绿+暖象牙，沉稳有呼吸 |
| 4 | 🍂 牛皮纸 | `kraft-paper.css` | 怀旧 / 人文 / 阅读 / 文学 | 深暖褐+牛皮米黄，焦糖点缀 |
| 5 | 🌙 沙丘 | `dune.css` | 艺术 / 设计 / 创意 / 时尚 | 炭褐+冷沙金，克制高级 |

---

## 🖋 墨水经典 (默认)

**适合**:通用分享、商业发布、科技产品、任何场景都安全的默认选择。
**调性**:纯墨黑 + 暖米白,冷灰蓝点缀,杂志感最强、最克制。
**流体背景**:墨黑底 + 冷灰蓝色散流。

```css
--ink:#0a0a0b;
--ink-rgb:10,10,11;
--paper:#f1efea;
--paper-rgb:241,239,234;
--paper-tint:#e8e5de;
--ink-tint:#18181a;
--accent:#4a5a6e;
--accent-2:#8a98aa;
```

---

## 🌊 靛蓝瓷 (Indigo Porcelain)

**适合**:科技/研究/数据分享、工程师文化、深度内容、技术发布会、理性叙事。
**调性**:深靛蓝 + 冷瓷白,蓝青花瓷感,冷静、理性、有深度。
**流体背景**:深靛蓝底 + 瓷蓝色散流。

```css
--ink:#0b1d3a;
--ink-rgb:11,29,58;
--paper:#eef2f6;
--paper-rgb:238,242,246;
--paper-tint:#dde4ec;
--ink-tint:#15294a;
--accent:#2f5fa8;
--accent-2:#6ea3d8;
```

---

## 🌿 森林墨 (Forest Ink)

**适合**:自然/可持续/文化/非虚构内容、户外品牌、环保主题。
**调性**:深森林墨绿 + 暖象牙,沉稳、有呼吸感、带泥土气。
**流体背景**:墨绿底 + 翠绿色散流。

```css
--ink:#16291c;
--ink-rgb:22,41,28;
--paper:#f3efe2;
--paper-rgb:243,239,226;
--paper-tint:#e8e2cf;
--ink-tint:#213a29;
--accent:#2d6a4f;
--accent-2:#7fb069;
```

---

## 🍂 牛皮纸 (Kraft Paper)

**适合**:怀旧/人文/阅读/历史/文学分享、独立杂志、手作品牌。
**调性**:深暖褐 + 牛皮米黄,焦糖点缀,像牛皮信封或老笔记本,温暖、有年代感。
**流体背景**:深褐底 + 焦糖色散流。

```css
--ink:#2a1e13;
--ink-rgb:42,30,19;
--paper:#eedfc7;
--paper-rgb:238,223,199;
--paper-tint:#e0d0b6;
--ink-tint:#3a2a1d;
--accent:#8b5e3c;
--accent-2:#c9a96e;
```

---

## 🌙 沙丘 (Dune)

**适合**:艺术/设计/创意/时尚分享、画廊手册、审美优先的私享会。
**调性**:炭褐 + 冷沙金,克制、高级、中性偏冷,像沙漠黄昏或建筑设计图册。与牛皮纸的区别：沙丘偏冷沙金、牛皮纸偏暖红褐。
**流体背景**:炭褐底 + 沙金色散流。

```css
--ink:#241e16;
--ink-rgb:36,30,22;
--paper:#ede4d1;
--paper-rgb:237,228,209;
--paper-tint:#ddd2b8;
--ink-tint:#322a20;
--accent:#b8860b;
--accent-2:#d4a853;
```

---

## 推荐选择参考

| 如果是... | 推荐主题 |
|---|---|
| 不知道选啥 / 第一次用 | 🖋 墨水经典 |
| AI / 技术 / 产品发布 | 🌊 靛蓝瓷 |
| 内容 / 行业观察 / 文化 | 🌿 森林墨 |
| 书评 / 生活方式 / 人文 | 🍂 牛皮纸 |
| 设计 / 艺术 / 品牌 | 🌙 沙丘 |

---

## 切换原则

- **一份 deck 只用一套主题**,不要中途换色
- WebGL shader 读取主题的 `--ink-rgb`/`--paper-rgb`/`--accent` 变量,每套主题的流体背景配色都不同(深蓝瓷/墨绿/暖褐/沙金/墨黑)
- `currentColor` 驱动的 border / icon 会跟随 section 的 text color 自动适配
- 预设主题可按 T 键实时切换 5 套主题（静态/微动/沉浸均支持）；自定义 `css/theme.css` 不参与热切换

## ❌ 不要做的事

- ❌ **不允许混搭**
- ❌ **不要把用户颜色散写进 HTML inline style**——明确品牌色必须先生成 deck 专属 `theme.css`
- ❌ **不要直接修改 base.css 的颜色**——所有散落 rgba 都走 var,改 theme.css 一处即可
