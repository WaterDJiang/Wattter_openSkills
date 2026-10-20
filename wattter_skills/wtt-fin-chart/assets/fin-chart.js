(function () {
  const palette = {
    growth: "#0f8b6f",
    profit: "#b7791f",
    risk: "#b64242",
    cash: "#3b6ea8",
    structure: "#6f5aa7",
    ink: "#151515",
    muted: "#6b665e",
    grid: "#d7d0c2",
    paper: "#fffaf0"
  };

  function last(values) {
    return Array.isArray(values) && values.length ? values[values.length - 1] : null;
  }

  function first(values) {
    return Array.isArray(values) && values.length ? values[0] : null;
  }

  function safeNumber(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function cagr(values) {
    const start = safeNumber(first(values));
    const end = safeNumber(last(values));
    const years = values.length - 1;
    if (!start || !end || years <= 0 || start <= 0) return null;
    return Math.pow(end / start, 1 / years) - 1;
  }

  function delta(values) {
    const start = safeNumber(first(values));
    const end = safeNumber(last(values));
    if (start === null || end === null) return null;
    return end - start;
  }

  function margin(numerator, denominator) {
    if (!denominator) return null;
    return numerator / denominator;
  }

  function metric(data, key) {
    return data && data.metrics && Array.isArray(data.metrics[key]) ? data.metrics[key] : [];
  }

  function valueAt(values, index) {
    return Array.isArray(values) && index >= 0 && index < values.length ? safeNumber(values[index]) : null;
  }

  function periodCount(data) {
    return Array.isArray(data.periods) ? data.periods.length : 0;
  }

  function latestIndex(data) {
    return Math.max(periodCount(data) - 1, 0);
  }

  function deriveByPeriod(data, fn) {
    return (data.periods || []).map((_, index) => fn(index));
  }

  function ratioSeries(numerator, denominator) {
    return numerator.map((value, index) => margin(value, denominator[index]));
  }

  function grossMarginSeries(data) {
    const direct = metric(data, "grossMargin");
    if (direct.length) return direct;
    const revenue = metric(data, "revenue");
    const grossProfit = metric(data, "grossProfit");
    return ratioSeries(grossProfit, revenue);
  }

  function operatingMarginSeries(data) {
    const direct = metric(data, "operatingMargin");
    if (direct.length) return direct;
    return ratioSeries(metric(data, "operatingIncome"), metric(data, "revenue"));
  }

  function netMarginSeries(data) {
    const direct = metric(data, "netMargin");
    if (direct.length) return direct;
    return ratioSeries(metric(data, "netIncome"), metric(data, "revenue"));
  }

  function fcfSeries(data) {
    const direct = metric(data, "fcf");
    if (direct.length) return direct;
    const operatingCashFlow = metric(data, "operatingCashFlow");
    const capex = metric(data, "capex");
    return deriveByPeriod(data, index => {
      const cfo = valueAt(operatingCashFlow, index);
      const capexValue = valueAt(capex, index);
      if (cfo === null || capexValue === null) return null;
      return cfo - Math.abs(capexValue);
    });
  }

  function expenseItems(data, index = latestIndex(data)) {
    const revenue = metric(data, "revenue");
    const grossProfit = metric(data, "grossProfit");
    const cogs = metric(data, "cogs");
    const source = [
      { name: "COGS", value: valueAt(cogs, index) ?? (valueAt(revenue, index) !== null && valueAt(grossProfit, index) !== null ? valueAt(revenue, index) - valueAt(grossProfit, index) : null) },
      { name: "Sales & marketing", value: valueAt(metric(data, "salesMarketing"), index) },
      { name: "R&D", value: valueAt(metric(data, "researchDevelopment"), index) },
      { name: "G&A", value: valueAt(metric(data, "generalAdmin"), index) },
      { name: "Other opex", value: valueAt(metric(data, "otherOpex"), index) }
    ];
    return source
      .map(item => ({ ...item, value: item.value === null ? null : Math.abs(item.value) }))
      .filter(item => item.value !== null && item.value > 0);
  }

  function fmtNumber(value, digits = 0) {
    const number = safeNumber(value);
    if (number === null) return "n/a";
    return new Intl.NumberFormat("en-US", {
      maximumFractionDigits: digits,
      minimumFractionDigits: digits
    }).format(number);
  }

  function fmtCompact(value, currency = "") {
    const number = safeNumber(value);
    if (number === null) return "n/a";
    const abs = Math.abs(number);
    const prefix = currency === "USD" ? "$" : currency === "CNY" ? "¥" : "";
    if (abs >= 1000) return `${prefix}${fmtNumber(number / 1000, 2)}B`;
    return `${prefix}${fmtNumber(number, 0)}M`;
  }

  function fmtPercent(value, digits = 1) {
    const number = safeNumber(value);
    if (number === null) return "n/a";
    return `${(number * 100).toFixed(digits)}%`;
  }

  function fmtPointDelta(value) {
    const number = safeNumber(value);
    if (number === null) return "n/a";
    const sign = number > 0 ? "+" : "";
    return `${sign}${(number * 100).toFixed(1)} pts`;
  }

  function baseOption() {
    return {
      color: [palette.growth, palette.profit, palette.cash, palette.structure, palette.risk],
      backgroundColor: "transparent",
      textStyle: {
        color: palette.ink,
        fontFamily: "Inter, Noto Sans SC, sans-serif"
      },
      grid: {
        top: 42,
        left: 54,
        right: 28,
        bottom: 42
      },
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(21, 21, 21, 0.92)",
        borderWidth: 0,
        textStyle: { color: "#fff" },
        valueFormatter: value => typeof value === "number" ? fmtNumber(value, 1) : value
      },
      legend: {
        top: 0,
        right: 0,
        icon: "roundRect",
        itemWidth: 10,
        itemHeight: 10,
        textStyle: {
          color: palette.muted,
          fontSize: 12
        }
      },
      xAxis: {
        axisLine: { lineStyle: { color: palette.grid } },
        axisTick: { show: false },
        axisLabel: { color: palette.muted, fontSize: 12 }
      },
      yAxis: {
        splitLine: { lineStyle: { color: palette.grid, type: "dashed" } },
        axisLabel: { color: palette.muted, fontSize: 12 }
      }
    };
  }

  function optionRevenueMargin(data) {
    const option = baseOption();
    const revenue = metric(data, "revenue");
    return {
      ...option,
      grid: { ...option.grid, right: 58 },
      legend: { ...option.legend, data: ["Revenue", "Gross margin", "Operating margin"] },
      xAxis: { ...option.xAxis, type: "category", data: data.periods },
      yAxis: [
        {
          ...option.yAxis,
          type: "value",
          name: data.unit || "",
          axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtCompact(value, data.currency) }
        },
        {
          ...option.yAxis,
          type: "value",
          min: 0,
          max: 1,
          axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtPercent(value, 0) }
        }
      ],
      series: [
        {
          name: "Revenue",
          type: "bar",
          barWidth: 28,
          data: revenue,
          itemStyle: { color: palette.growth, borderRadius: [4, 4, 0, 0] },
          label: {
            show: true,
            position: "top",
            color: palette.ink,
            fontSize: 11,
            formatter: params => fmtCompact(params.value, data.currency)
          }
        },
        {
          name: "Gross margin",
          type: "line",
          yAxisIndex: 1,
          smooth: true,
          symbolSize: 8,
          lineStyle: { width: 3, color: palette.profit },
          itemStyle: { color: palette.profit },
          data: grossMarginSeries(data)
        },
        {
          name: "Operating margin",
          type: "line",
          yAxisIndex: 1,
          smooth: true,
          symbolSize: 8,
          lineStyle: { width: 3, color: palette.cash },
          itemStyle: { color: palette.cash },
          data: operatingMarginSeries(data)
        }
      ]
    };
  }

  function optionSegmentMix(data) {
    const option = baseOption();
    const segments = data.segments || [];
    return {
      ...option,
      grid: { top: 36, left: 42, right: 16, bottom: 42 },
      legend: { ...option.legend, top: 0, left: 0 },
      xAxis: { ...option.xAxis, type: "category", data: data.periods },
      yAxis: {
        ...option.yAxis,
        type: "value",
        axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtCompact(value, data.currency) }
      },
      series: segments.map((segment, index) => ({
        name: segment.name,
        type: "bar",
        stack: "segment",
        barWidth: 30,
        data: segment.values,
        itemStyle: {
          color: [palette.structure, palette.profit, palette.cash, palette.growth][index % 4],
          borderRadius: index === segments.length - 1 ? [4, 4, 0, 0] : 0
        }
      }))
    };
  }

  function optionCashFlow(data) {
    const option = baseOption();
    const fcf = fcfSeries(data);
    const revenue = metric(data, "revenue");
    const marginValues = fcf.map((value, index) => margin(value, revenue[index]));
    return {
      ...option,
      grid: { ...option.grid, right: 58 },
      legend: { ...option.legend, data: ["Free cash flow", "FCF margin"] },
      xAxis: { ...option.xAxis, type: "category", data: data.periods },
      yAxis: [
        {
          ...option.yAxis,
          type: "value",
          axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtCompact(value, data.currency) }
        },
        {
          ...option.yAxis,
          type: "value",
          axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtPercent(value, 0) }
        }
      ],
      series: [
        {
          name: "Free cash flow",
          type: "bar",
          barWidth: 30,
          data: fcf,
          itemStyle: { color: palette.cash, borderRadius: [4, 4, 0, 0] }
        },
        {
          name: "FCF margin",
          type: "line",
          yAxisIndex: 1,
          smooth: true,
          symbolSize: 8,
          data: marginValues,
          lineStyle: { width: 3, color: palette.growth },
          itemStyle: { color: palette.growth }
        }
      ]
    };
  }

  function optionWaterfall(items) {
    const option = baseOption();
    let running = 0;
    const transparent = [];
    const values = [];
    items.forEach((item, index) => {
      if (index === 0 || item.total) {
        transparent.push(0);
        values.push(item.value);
        running = item.value;
      } else if (item.value >= 0) {
        transparent.push(running);
        values.push(item.value);
        running += item.value;
      } else {
        transparent.push(running + item.value);
        values.push(Math.abs(item.value));
        running += item.value;
      }
    });
    return {
      ...option,
      legend: { show: false },
      xAxis: { ...option.xAxis, type: "category", data: items.map(item => item.name) },
      yAxis: {
        ...option.yAxis,
        type: "value",
        axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtNumber(value, 0) }
      },
      series: [
        {
          type: "bar",
          stack: "bridge",
          itemStyle: { color: "transparent" },
          emphasis: { itemStyle: { color: "transparent" } },
          data: transparent
        },
        {
          type: "bar",
          stack: "bridge",
          barWidth: 28,
          data: values,
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: params => {
              const item = items[params.dataIndex];
              if (params.dataIndex === 0 || item.total) return palette.ink;
              return item.value >= 0 ? palette.growth : palette.risk;
            }
          },
          label: {
            show: true,
            position: "top",
            color: palette.ink,
            fontSize: 11,
            formatter: params => {
              const item = items[params.dataIndex];
              if (params.dataIndex === 0 || item.total) return fmtNumber(item.value, 0);
              return `${item.value > 0 ? "+" : ""}${fmtNumber(item.value, 0)}`;
            }
          }
        }
      ]
    };
  }

  function optionPnlCommonSize(data) {
    const option = baseOption();
    const revenue = metric(data, "revenue");
    const items = [
      { name: "COGS", values: deriveByPeriod(data, index => valueAt(metric(data, "cogs"), index) ?? (valueAt(revenue, index) !== null && valueAt(metric(data, "grossProfit"), index) !== null ? valueAt(revenue, index) - valueAt(metric(data, "grossProfit"), index) : null)), color: palette.risk },
      { name: "Sales & marketing", values: metric(data, "salesMarketing"), color: palette.cash },
      { name: "R&D", values: metric(data, "researchDevelopment"), color: palette.structure },
      { name: "G&A", values: metric(data, "generalAdmin"), color: palette.profit }
    ].filter(item => item.values.some(value => safeNumber(value) !== null));
    return {
      ...option,
      grid: { ...option.grid, right: 26, bottom: 44 },
      legend: { ...option.legend, data: [...items.map(item => item.name), "Operating margin"] },
      tooltip: {
        ...option.tooltip,
        valueFormatter: value => typeof value === "number" ? fmtPercent(value, 1) : value
      },
      xAxis: { ...option.xAxis, type: "category", data: data.periods },
      yAxis: {
        ...option.yAxis,
        type: "value",
        axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtPercent(value, 0) }
      },
      series: [
        ...items.map(item => ({
          name: item.name,
          type: "bar",
          stack: "cost",
          barWidth: 30,
          data: item.values.map((value, index) => {
            const denominator = valueAt(revenue, index);
            if (value === null || denominator === null) return null;
            return -Math.abs(value) / denominator;
          }),
          itemStyle: { color: item.color }
        })),
        {
          name: "Operating margin",
          type: "line",
          smooth: true,
          symbolSize: 8,
          data: operatingMarginSeries(data),
          lineStyle: { width: 3, color: palette.growth },
          itemStyle: { color: palette.growth },
          label: {
            show: true,
            position: "top",
            color: palette.ink,
            fontSize: 11,
            formatter: params => params.dataIndex === data.periods.length - 1 ? fmtPercent(params.value, 1) : ""
          }
        }
      ]
    };
  }

  function optionExpenseMix(data) {
    const option = baseOption();
    const index = latestIndex(data);
    const items = expenseItems(data, index);
    const period = data.periods && data.periods[index] ? data.periods[index] : "Latest";
    return {
      ...option,
      legend: { ...option.legend, orient: "vertical", left: 0, top: 0 },
      tooltip: {
        trigger: "item",
        backgroundColor: "rgba(21, 21, 21, 0.92)",
        borderWidth: 0,
        textStyle: { color: "#fff" },
        formatter: params => `${params.name}<br>${fmtCompact(params.value, data.currency)} · ${params.percent}%`
      },
      series: [
        {
          name: `${period} expense mix`,
          type: "pie",
          radius: ["46%", "72%"],
          center: ["56%", "54%"],
          minAngle: 8,
          avoidLabelOverlap: true,
          itemStyle: {
            borderColor: palette.paper,
            borderWidth: 3
          },
          label: {
            color: palette.ink,
            fontSize: 12,
            formatter: "{b}\n{d}%"
          },
          data: items.map((item, itemIndex) => ({
            name: item.name,
            value: item.value,
            itemStyle: { color: [palette.risk, palette.cash, palette.structure, palette.profit, palette.muted][itemIndex % 5] }
          }))
        }
      ]
    };
  }

  function optionBalanceSheetStructure(data) {
    const option = baseOption();
    const detailedRows = [
      { name: "Current assets", key: "currentAssets", stack: "Assets", color: palette.growth },
      { name: "Non-current assets", key: "nonCurrentAssets", stack: "Assets", color: palette.cash },
      { name: "Current liabilities", key: "currentLiabilities", stack: "Funding", color: palette.risk },
      { name: "Non-current liabilities", key: "nonCurrentLiabilities", stack: "Funding", color: "#8d4f4f" },
      { name: "Equity", key: "shareholdersEquity", stack: "Funding", color: palette.structure }
    ].filter(row => metric(data, row.key).some(value => safeNumber(value) !== null));
    const rows = detailedRows.length ? detailedRows : [
      { name: "Total assets", key: "totalAssets", stack: "Assets", color: palette.cash },
      { name: "Total liabilities", key: "totalLiabilities", stack: "Funding", color: palette.risk },
      { name: "Equity", key: "shareholdersEquity", stack: "Funding", color: palette.structure }
    ].filter(row => metric(data, row.key).some(value => safeNumber(value) !== null));
    return {
      ...option,
      grid: { ...option.grid, right: 22, bottom: 44 },
      legend: { ...option.legend, data: rows.map(row => row.name) },
      xAxis: { ...option.xAxis, type: "category", data: data.periods },
      yAxis: {
        ...option.yAxis,
        type: "value",
        axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtCompact(value, data.currency) }
      },
      series: rows.map(row => ({
        name: row.name,
        type: "bar",
        stack: row.stack,
        barWidth: 18,
        emphasis: { focus: "series" },
        data: metric(data, row.key),
        itemStyle: { color: row.color, borderRadius: [3, 3, 0, 0] }
      }))
    };
  }

  function optionCashFlowStatement(data) {
    const option = baseOption();
    const operatingCashFlow = metric(data, "operatingCashFlow");
    const investingCashFlow = metric(data, "investingCashFlow");
    const financingCashFlow = metric(data, "financingCashFlow");
    const netCashChange = deriveByPeriod(data, index => {
      const values = [valueAt(operatingCashFlow, index), valueAt(investingCashFlow, index), valueAt(financingCashFlow, index)];
      if (values.every(value => value === null)) return null;
      return values.reduce((sum, value) => sum + (value || 0), 0);
    });
    return {
      ...option,
      grid: { ...option.grid, right: 58, bottom: 44 },
      legend: { ...option.legend, data: ["CFO", "Investing CF", "Financing CF", "Net cash change"] },
      xAxis: { ...option.xAxis, type: "category", data: data.periods },
      yAxis: {
        ...option.yAxis,
        type: "value",
        axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtCompact(value, data.currency) }
      },
      series: [
        { name: "CFO", type: "bar", barWidth: 18, data: operatingCashFlow, itemStyle: { color: palette.growth, borderRadius: [3, 3, 0, 0] } },
        { name: "Investing CF", type: "bar", barWidth: 18, data: investingCashFlow, itemStyle: { color: palette.risk, borderRadius: [3, 3, 0, 0] } },
        { name: "Financing CF", type: "bar", barWidth: 18, data: financingCashFlow, itemStyle: { color: palette.structure, borderRadius: [3, 3, 0, 0] } },
        {
          name: "Net cash change",
          type: "line",
          smooth: true,
          symbolSize: 8,
          data: netCashChange,
          lineStyle: { width: 3, color: palette.ink },
          itemStyle: { color: palette.ink }
        }
      ]
    };
  }

  function optionMarginLadder(data) {
    const option = baseOption();
    const fcf = fcfSeries(data);
    const revenue = metric(data, "revenue");
    return {
      ...option,
      grid: { ...option.grid, right: 24, bottom: 44 },
      legend: { ...option.legend, data: ["Gross margin", "Operating margin", "Net margin", "FCF margin"] },
      tooltip: {
        ...option.tooltip,
        valueFormatter: value => typeof value === "number" ? fmtPercent(value, 1) : value
      },
      xAxis: { ...option.xAxis, type: "category", data: data.periods },
      yAxis: {
        ...option.yAxis,
        type: "value",
        axisLabel: { ...option.yAxis.axisLabel, formatter: value => fmtPercent(value, 0) }
      },
      series: [
        { name: "Gross margin", type: "line", smooth: true, symbolSize: 7, data: grossMarginSeries(data), lineStyle: { width: 3, color: palette.profit }, itemStyle: { color: palette.profit } },
        { name: "Operating margin", type: "line", smooth: true, symbolSize: 7, data: operatingMarginSeries(data), lineStyle: { width: 3, color: palette.growth }, itemStyle: { color: palette.growth } },
        { name: "Net margin", type: "line", smooth: true, symbolSize: 7, data: netMarginSeries(data), lineStyle: { width: 3, color: palette.structure }, itemStyle: { color: palette.structure } },
        { name: "FCF margin", type: "line", smooth: true, symbolSize: 7, data: fcf.map((value, index) => margin(value, revenue[index])), lineStyle: { width: 3, color: palette.cash }, itemStyle: { color: palette.cash } }
      ]
    };
  }

  function optionRatioTrend(data) {
    const option = baseOption();
    const ratios = [
      { name: "Current ratio", values: metric(data, "currentRatio").length ? metric(data, "currentRatio") : ratioSeries(metric(data, "currentAssets"), metric(data, "currentLiabilities")), color: palette.growth },
      { name: "Debt / equity", values: metric(data, "debtToEquity").length ? metric(data, "debtToEquity") : ratioSeries(metric(data, "totalDebt"), metric(data, "shareholdersEquity")), color: palette.risk },
      { name: "Asset turnover", values: metric(data, "assetTurnover").length ? metric(data, "assetTurnover") : ratioSeries(metric(data, "revenue"), metric(data, "totalAssets")), color: palette.cash }
    ].filter(row => row.values.some(value => safeNumber(value) !== null));
    return {
      ...option,
      grid: { ...option.grid, right: 24, bottom: 44 },
      legend: { ...option.legend, data: ratios.map(row => row.name) },
      tooltip: {
        ...option.tooltip,
        valueFormatter: value => typeof value === "number" ? `${fmtNumber(value, 2)}x` : value
      },
      xAxis: { ...option.xAxis, type: "category", data: data.periods },
      yAxis: {
        ...option.yAxis,
        type: "value",
        axisLabel: { ...option.yAxis.axisLabel, formatter: value => `${fmtNumber(value, 1)}x` }
      },
      series: ratios.map(row => ({
        name: row.name,
        type: "line",
        smooth: true,
        symbolSize: 8,
        data: row.values,
        lineStyle: { width: 3, color: row.color },
        itemStyle: { color: row.color }
      }))
    };
  }

  function render(id, option) {
    const element = document.getElementById(id);
    if (!element) return null;
    if (!window.echarts) {
      element.innerHTML = '<div class="chart-empty">ECharts failed to load.<br>Use a local copy or replace the CDN URL.</div>';
      return null;
    }
    const chart = echarts.init(element, null, { renderer: "canvas" });
    chart.setOption(option);
    window.addEventListener("resize", () => chart.resize());
    return chart;
  }

  function metricCard(label, value, deltaText, note, tone = "growth") {
    return `
      <article class="metric-card">
        <div>
          <div class="label">${label}</div>
          <div class="value">${value}</div>
        </div>
        <div>
          <div class="delta" style="color: var(--${tone})">${deltaText}</div>
          <div class="note">${note}</div>
        </div>
      </article>
    `;
  }

  function renderTemplateReport(data) {
    const revenue = metric(data, "revenue");
    const grossMargins = grossMarginSeries(data);
    const operatingMargins = operatingMarginSeries(data);
    const fcf = fcfSeries(data);
    const revenueCagr = cagr(revenue);
    const grossMarginDelta = delta(grossMargins);
    const opMarginDelta = delta(operatingMargins);
    const fcfMarginValues = fcf.map((value, index) => margin(value, revenue[index]));
    const fcfMarginDelta = delta(fcfMarginValues);

    const metricStrip = document.getElementById("metricStrip");
    if (metricStrip) {
      metricStrip.innerHTML = [
        metricCard("Revenue CAGR", fmtPercent(revenueCagr), `${fmtCompact(first(revenue), data.currency)} to ${fmtCompact(last(revenue), data.currency)}`, "Top-line compounding across the displayed period."),
        metricCard("Gross margin", fmtPercent(last(grossMargins)), fmtPointDelta(grossMarginDelta), "Mix, pricing, or delivery efficiency improved."),
        metricCard("Operating margin", fmtPercent(last(operatingMargins)), fmtPointDelta(opMarginDelta), "Operating leverage is visible below gross profit."),
        metricCard("FCF margin", fmtPercent(last(fcfMarginValues)), fmtPointDelta(fcfMarginDelta), "Cash conversion is improving with scale.", "cash")
      ].join("");
    }

    const period = document.getElementById("periodLabel");
    if (period) period.textContent = data.periodLabel || `${first(data.periods)}-${last(data.periods)}`;
    const source = document.getElementById("sourceLabel");
    if (source) source.textContent = data.source || "Source not specified";
    const unit = document.getElementById("unitLabel");
    if (unit) unit.textContent = `${data.currency || ""} ${data.unit || ""}`.trim();
    const assumptions = document.getElementById("assumptionText");
    if (assumptions) assumptions.textContent = (data.assumptions || []).join(". ");

    render("chartRevenueMargin", optionRevenueMargin(data));
    render("chartSegmentMix", optionSegmentMix(data));
    render("chartCashFlow", optionCashFlow(data));
    render("chartBridge", optionWaterfall(data.bridge || []));
    render("chartPnlCommonSize", optionPnlCommonSize(data));
    render("chartExpenseMix", optionExpenseMix(data));
    render("chartBalanceSheet", optionBalanceSheetStructure(data));
    render("chartCashFlowStatement", optionCashFlowStatement(data));
    render("chartMarginLadder", optionMarginLadder(data));
    render("chartRatioTrend", optionRatioTrend(data));
  }

  window.FinChart = {
    palette,
    cagr,
    delta,
    margin,
    fmtNumber,
    fmtCompact,
    fmtPercent,
    fmtPointDelta,
    optionRevenueMargin,
    optionSegmentMix,
    optionCashFlow,
    optionWaterfall,
    optionPnlCommonSize,
    optionExpenseMix,
    optionBalanceSheetStructure,
    optionCashFlowStatement,
    optionMarginLadder,
    optionRatioTrend,
    render,
    renderTemplateReport
  };
})();
