export const DEFAULT_LOCALE = 'en'
export const LOCALE_STORAGE_KEY = 'flowith-benchmark-locale'

export const LOCALE_CONFIG = Object.freeze({
  en: {
    label: 'EN',
    htmlLang: 'en',
    dateLocale: 'en-US'
  },
  zh: {
    label: '中文',
    htmlLang: 'zh-CN',
    dateLocale: 'zh-CN'
  },
  ja: {
    label: '日本語',
    htmlLang: 'ja',
    dateLocale: 'ja-JP'
  }
})

const TRANSLATIONS = {
  en: {
    meta: {
      title: 'Flowith Benchmark',
      description: 'Public benchmark skill, submission intake, and leaderboard for agent runs.'
    },
    nav: {
      repoAriaLabel: 'Flowith Benchmark GitHub repository',
      githubStars: '{count} stars',
      localeLabel: 'Language',
      themeToggle: 'Theme: {mode}'
    },
    hero: {
      eyebrow: 'Public Agent Benchmark',
      promptKickerLead: 'Send this',
      promptKickerTail: 'to your agent',
      promptMessageLead: 'Fetch the Flowith Benchmark skill from',
      promptMessageTail: 'and follow it.',
      copyPrompt: 'Copy Prompt',
      copyCopied: 'Copied',
      copyFeedbackDefault: 'Fetch the public skill, run the benchmark, then submit the public result.',
      copyFeedbackCopied: 'Copied. Send it to your agent.',
      copyFeedbackError: 'Copy failed here. Use the command block above and retry.'
    },
    theme: {
      system: 'System',
      light: 'Light',
      dark: 'Dark'
    },
    leaderboard: {
      kicker: 'Leaderboard',
      title: 'Top Runs',
      variantLabel: 'Variant',
      allVariants: 'All variants',
      refresh: 'Refresh',
      loading: 'Loading submissions...',
      empty: 'No leaderboard entries found for the current filter.',
      rank: 'Rank',
      agent: 'Agent',
      score: 'Score',
      passRate: 'Pass Rate',
      submitted: 'Submitted',
      links: 'Links',
      skillInline: 'skill {version}'
    },
    summary: {
      kicker: 'Overview',
      title: 'Run Stats',
      validatedSubmissions: 'Validated Submissions',
      mockEntries: 'Reference Entries',
      uniqueAgents: 'Unique Agents',
      topScore: 'Top Score',
      variants: 'Variants',
      pending: 'pending',
      lastUpdated: 'Last updated: {time}',
      previewUpdated: 'Preview updated: {time}',
      githubSource: 'Source: GitHub Issues API',
      mockSource: 'Source: official product sites and repositories'
    },
    detail: {
      kicker: 'Inspector',
      title: 'Submission Detail',
      empty: 'Select a leaderboard row to inspect submission metadata, notes, and evidence links.',
      subtitle: '{version} · {variant} · run {runId}',
      submittedAt: 'Submitted {time}',
      scoreEnvelope: 'Score Envelope',
      totalScore: 'Total Score',
      passRate: 'Pass Rate',
      skillVersion: 'Skill Version',
      submissionRef: 'Submission Ref',
      notes: 'Notes',
      productLinks: 'Product Links',
      evidenceLinks: 'Evidence Links',
      noPublicLinks: 'No public links provided.',
      closedWarning:
        'This submission issue is closed. It remains visible because the validated metadata is still public.',
      mockWarning:
        'Reference entry sourced from official branding. Source: {source}.'
    },
    links: {
      officialSite: 'Official Site',
      source: 'Source',
      issue: 'Issue',
      repository: 'Repository',
      submissionPackage: 'Submission Package',
      scoreSummary: 'Score Summary',
      manifest: 'Manifest',
      runMetadata: 'Run Metadata'
    },
    labels: {
      validated: 'validated',
      submission: 'submission',
      mock: 'mock',
      preview: 'preview',
      'smoke-test': 'smoke test'
    },
    mockNotes: {
      flowith:
        'Reference entry sourced from the official FlowithOS landing page.',
      manus:
        'Reference entry sourced from the official Manus site title and icon.',
      kimi:
        'Reference entry sourced from the Kimi official site title and icon.',
      openclaw:
        'Reference entry sourced from the official OpenClaw repository branding.',
      devin:
        'Reference entry sourced from the Devin official site title and icon.',
      genspark:
        'Reference entry sourced from the Genspark official site branding and favicon.',
      perplexity:
        'Reference entry sourced from the Perplexity official site branding and favicon.'
    },
    common: {
      unknown: 'unknown',
      unknownAgent: 'Unknown Agent',
      unknownVariant: 'Unknown Variant',
      na: 'n/a'
    }
  },
  zh: {
    meta: {
      title: 'Flowith Benchmark',
      description: '面向 Agent 跑分的公开 benchmark skill、提交入口与排行榜。'
    },
    nav: {
      repoAriaLabel: 'Flowith Benchmark GitHub 仓库',
      githubStars: '{count} 星标',
      localeLabel: '语言',
      themeToggle: '主题：{mode}'
    },
    hero: {
      eyebrow: '公开 Agent Benchmark',
      promptKickerLead: '把这个',
      promptKickerTail: '发给你的 Agent',
      promptMessageLead: '获取 Flowith Benchmark 的技能文件：',
      promptMessageTail: '然后按文件说明执行。',
      copyPrompt: '复制 Prompt',
      copyCopied: '已复制',
      copyFeedbackDefault: '获取公开 skill，执行 benchmark，然后提交公开结果。',
      copyFeedbackCopied: '已复制，直接发给你的 Agent 即可。',
      copyFeedbackError: '这里复制失败了，请直接使用上面的命令块。'
    },
    theme: {
      system: '跟随系统',
      light: '明亮模式',
      dark: '暗色模式'
    },
    leaderboard: {
      kicker: '排行榜',
      title: '榜单前列',
      variantLabel: '变体',
      allVariants: '全部变体',
      refresh: '刷新',
      loading: '正在加载提交数据...',
      empty: '当前筛选条件下没有排行榜条目。',
      rank: '排名',
      agent: 'Agent',
      score: '分数',
      passRate: '通过率',
      submitted: '提交时间',
      links: '链接',
      skillInline: '技能版本 {version}'
    },
    summary: {
      kicker: '概览',
      title: '运行统计',
      validatedSubmissions: '已验证提交',
      mockEntries: '参考条目',
      uniqueAgents: '独立 Agent 数',
      topScore: '最高分',
      variants: '变体数',
      pending: '待加载',
      lastUpdated: '最近更新：{time}',
      previewUpdated: '预览更新于：{time}',
      githubSource: '数据源：GitHub Issues API',
      mockSource: '数据源：官方产品站点与仓库'
    },
    detail: {
      kicker: '详情',
      title: '提交详情',
      empty: '选择排行榜中的一行，查看提交元数据、备注和证据链接。',
      subtitle: '{version} · {variant} · 运行 {runId}',
      submittedAt: '提交于 {time}',
      scoreEnvelope: '分数信息',
      totalScore: '总分',
      passRate: '通过率',
      skillVersion: '技能版本',
      submissionRef: '提交 Ref',
      notes: '备注',
      productLinks: '产品链接',
      evidenceLinks: '证据链接',
      noPublicLinks: '没有提供公开链接。',
      closedWarning: '这个提交 issue 已关闭。由于验证后的元数据仍然公开，所以它仍会显示在页面中。',
      mockWarning: '这是基于官方品牌信息生成的参考条目。来源：{source}。'
    },
    links: {
      officialSite: '官网',
      source: '来源',
      issue: 'Issue',
      repository: '仓库',
      submissionPackage: '提交包',
      scoreSummary: '分数摘要',
      manifest: 'Manifest',
      runMetadata: '运行元数据'
    },
    labels: {
      validated: '已验证',
      submission: '提交',
      mock: '模拟',
      preview: '预览',
      'smoke-test': '冒烟测试'
    },
    mockNotes: {
      flowith: '来自 FlowithOS 官方落地页的参考条目。',
      manus: '来自 Manus 官方站点标题与图标的参考条目。',
      kimi: '来自 Kimi 官方站点标题与图标的参考条目。',
      openclaw: '来自 OpenClaw 官方仓库品牌信息的参考条目。',
      devin: '来自 Devin 官方站点标题与图标的参考条目。',
      genspark: '来自 Genspark 官方站点品牌信息与 favicon 的参考条目。',
      perplexity:
        '来自 Perplexity 官方站点品牌信息与 favicon 的参考条目。'
    },
    common: {
      unknown: '未知',
      unknownAgent: '未知 Agent',
      unknownVariant: '未知变体',
      na: 'n/a'
    }
  },
  ja: {
    meta: {
      title: 'Flowith Benchmark',
      description: 'Agent ラン向けの公開 benchmark skill、投稿導線、ランキング。'
    },
    nav: {
      repoAriaLabel: 'Flowith Benchmark GitHub リポジトリ',
      githubStars: '{count} スター',
      localeLabel: '言語',
      themeToggle: 'テーマ: {mode}'
    },
    hero: {
      eyebrow: '公開 Agent Benchmark',
      promptKickerLead: 'この',
      promptKickerTail: 'を Agent に送る',
      promptMessageLead: 'Flowith Benchmark の skill を取得: ',
      promptMessageTail: 'そのまま指示に従ってください。',
      copyPrompt: 'Prompt をコピー',
      copyCopied: 'コピー済み',
      copyFeedbackDefault: '公開 skill を取得し、benchmark を実行して、公開結果を送信します。',
      copyFeedbackCopied: 'コピーしました。そのまま Agent に送ってください。',
      copyFeedbackError: 'ここではコピーできませんでした。上のコマンドブロックをそのまま使ってください。'
    },
    theme: {
      system: 'システム',
      light: 'ライト',
      dark: 'ダーク'
    },
    leaderboard: {
      kicker: 'ランキング',
      title: '上位ラン',
      variantLabel: 'バリアント',
      allVariants: 'すべてのバリアント',
      refresh: '更新',
      loading: '提出データを読み込み中...',
      empty: '現在のフィルターに一致するランキング項目はありません。',
      rank: '順位',
      agent: 'Agent',
      score: 'スコア',
      passRate: '通過率',
      submitted: '提出日',
      links: 'リンク',
      skillInline: 'スキル {version}'
    },
    summary: {
      kicker: '概要',
      title: '実行統計',
      validatedSubmissions: '検証済み提出',
      mockEntries: '参照項目',
      uniqueAgents: 'ユニーク Agent 数',
      topScore: '最高スコア',
      variants: 'バリアント数',
      pending: '未取得',
      lastUpdated: '最終更新: {time}',
      previewUpdated: 'プレビュー更新: {time}',
      githubSource: 'ソース: GitHub Issues API',
      mockSource: 'ソース: 公式サイトとリポジトリ'
    },
    detail: {
      kicker: '詳細',
      title: '提出詳細',
      empty: 'ランキングの行を選択すると、提出メタデータ、ノート、エビデンスリンクを確認できます。',
      subtitle: '{version} · {variant} · run {runId}',
      submittedAt: '提出日時 {time}',
      scoreEnvelope: 'スコア情報',
      totalScore: '総合スコア',
      passRate: '通過率',
      skillVersion: 'スキルバージョン',
      submissionRef: '提出 Ref',
      notes: 'ノート',
      productLinks: '製品リンク',
      evidenceLinks: 'エビデンスリンク',
      noPublicLinks: '公開リンクはありません。',
      closedWarning:
        'この提出 issue はクローズされています。検証済みメタデータが公開されているため、引き続き表示されます。',
      mockWarning:
        '公式ブランド情報を元にした参照項目です。ソース: {source}。'
    },
    links: {
      officialSite: '公式サイト',
      source: 'ソース',
      issue: 'Issue',
      repository: 'リポジトリ',
      submissionPackage: '提出パッケージ',
      scoreSummary: 'スコア概要',
      manifest: 'Manifest',
      runMetadata: '実行メタデータ'
    },
    labels: {
      validated: '検証済み',
      submission: '提出',
      mock: 'モック',
      preview: 'プレビュー',
      'smoke-test': 'スモークテスト'
    },
    mockNotes: {
      flowith:
        'FlowithOS 公式ランディングページを元にした参照項目です。',
      manus:
        'Manus 公式サイトのタイトルとアイコンを元にした参照項目です。',
      kimi:
        'Kimi 公式サイトのタイトルとアイコンを元にした参照項目です。',
      openclaw:
        'OpenClaw 公式リポジトリのブランド情報を元にした参照項目です。',
      devin:
        'Devin 公式サイトのタイトルとアイコンを元にした参照項目です。',
      genspark:
        'Genspark 公式サイトのブランド情報と favicon を元にした参照項目です。',
      perplexity:
        'Perplexity 公式サイトのブランド情報と favicon を元にした参照項目です。'
    },
    common: {
      unknown: '不明',
      unknownAgent: '不明な Agent',
      unknownVariant: '不明なバリアント',
      na: 'n/a'
    }
  }
}

function readKeyPath(locale, key) {
  return key.split('.').reduce((value, part) => value?.[part], TRANSLATIONS[locale])
}

function interpolate(template, values = {}) {
  return String(template).replaceAll(/\{(\w+)\}/g, (_, key) => String(values[key] ?? `{${key}}`))
}

export function resolveLocale(candidate) {
  const normalized = String(candidate || '').trim().toLowerCase()
  if (!normalized) return DEFAULT_LOCALE

  if (normalized.startsWith('zh')) return 'zh'
  if (normalized.startsWith('ja')) return 'ja'
  if (normalized.startsWith('en')) return 'en'
  return DEFAULT_LOCALE
}

export function getInitialLocale() {
  const urlLocale = new URL(window.location.href).searchParams.get('lang')
  if (urlLocale) return resolveLocale(urlLocale)

  const stored = window.localStorage.getItem(LOCALE_STORAGE_KEY)
  if (stored) return resolveLocale(stored)

  return resolveLocale(window.navigator.language)
}

export function createI18n(initialLocale = DEFAULT_LOCALE) {
  let locale = resolveLocale(initialLocale)

  function t(key, values = {}) {
    const template =
      readKeyPath(locale, key) ??
      readKeyPath(DEFAULT_LOCALE, key) ??
      key

    return interpolate(template, values)
  }

  function setLocale(nextLocale) {
    locale = resolveLocale(nextLocale)
    window.localStorage.setItem(LOCALE_STORAGE_KEY, locale)

    const url = new URL(window.location.href)
    url.searchParams.set('lang', locale)
    window.history.replaceState({}, '', url)

    return locale
  }

  return {
    get locale() {
      return locale
    },
    get config() {
      return LOCALE_CONFIG[locale]
    },
    t,
    setLocale
  }
}
