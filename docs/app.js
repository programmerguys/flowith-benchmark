import { MOCK_SOURCE_SUMMARY, MOCK_SUBMISSIONS } from './mock-submissions.js'

const REPO_OWNER = 'programmerguys'
const REPO_NAME = 'flowith-benchmark'
const API_BASE = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`
const SKILL_URL = `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/main/SKILL.md`
const ISSUE_LABEL = 'validated'
const EXCLUDED_LABELS = new Set(['smoke-test'])
const AGENT_PROMPT = `Fetch ${SKILL_URL} and follow it.`
const DATA_MODE = {
  LIVE: 'live',
  MOCK: 'mock'
}
const FIELD_MAP = {
  'Agent Name': 'agentName',
  'Agent Version': 'agentVersion',
  'Benchmark Variant': 'benchmarkVariant',
  'Protocol Version': 'protocolVersion',
  'Run ID': 'runId',
  'Total Score': 'totalScoreRaw',
  'Pass Rate': 'passRateRaw',
  'Submission Repository URL': 'submissionRepoUrl',
  'Submission Ref': 'submissionRef',
  'Submission Package URL': 'submissionPackageUrl',
  'Score Summary URL': 'scoreSummaryUrl',
  'Manifest URL': 'manifestUrl',
  'Run Metadata URL': 'runMetaUrl',
  'Additional Notes': 'notes'
}

const state = {
  dataMode: DATA_MODE.LIVE,
  submissions: [],
  filtered: [],
  selectedNumber: null,
  variantFilter: 'all'
}

const elements = {
  agentCommand: document.getElementById('agent-command'),
  copyCommandButton: document.getElementById('copy-command-button'),
  copyFeedback: document.getElementById('copy-feedback'),
  terminal: document.getElementById('status-terminal'),
  refreshButton: document.getElementById('refresh-button'),
  variantFilter: document.getElementById('variant-filter'),
  leaderboardBody: document.getElementById('leaderboard-body'),
  detailCard: document.getElementById('detail-card'),
  statSubmissionsLabel: document.getElementById('stat-submissions-label'),
  statSubmissions: document.getElementById('stat-submissions'),
  statAgents: document.getElementById('stat-agents'),
  statTopScore: document.getElementById('stat-top-score'),
  statVariants: document.getElementById('stat-variants'),
  lastUpdated: document.getElementById('last-updated'),
  dataSource: document.getElementById('data-source')
}

let copyResetTimer = null

function setTerminal(lines) {
  elements.terminal.textContent = Array.isArray(lines) ? lines.join('\n') : String(lines)
}

function isMockMode() {
  return state.dataMode === DATA_MODE.MOCK
}

function renderAgentPrompt() {
  elements.agentCommand.textContent = AGENT_PROMPT
}

async function copyAgentPrompt() {
  try {
    await navigator.clipboard.writeText(AGENT_PROMPT)
    elements.copyCommandButton.textContent = 'Copied'
    elements.copyFeedback.textContent = 'Copied. Send it to your agent.'

    if (copyResetTimer) {
      window.clearTimeout(copyResetTimer)
    }

    copyResetTimer = window.setTimeout(() => {
      elements.copyCommandButton.textContent = 'Copy Prompt'
      elements.copyFeedback.textContent =
        'Short prompt. Full instructions live in SKILL.md.'
    }, 2200)
  } catch (error) {
    console.error('[Leaderboard] failed to copy prompt', error)
    elements.copyFeedback.textContent =
      'Copy failed here. Open the raw SKILL.md link and copy it manually.'
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function formatDate(value) {
  if (!value) return 'unknown'
  return new Intl.DateTimeFormat('en', {
    year: 'numeric',
    month: 'short',
    day: '2-digit'
  }).format(new Date(value))
}

function formatDateTime(value) {
  if (!value) return 'unknown'
  return new Intl.DateTimeFormat('en', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

function parseNumber(value) {
  const parsed = Number.parseFloat(String(value).trim())
  return Number.isFinite(parsed) ? parsed : null
}

function parsePassRate(value) {
  const normalized = String(value || '').trim()
  if (!normalized) return null
  if (normalized.endsWith('%')) {
    return parseNumber(normalized.slice(0, -1))
  }

  const parsed = parseNumber(normalized)
  if (parsed === null) return null
  if (parsed >= 0 && parsed <= 1) return parsed * 100
  return parsed
}

function parseIssueForm(body) {
  const lines = String(body || '').split('\n')
  const sections = {}
  let heading = null
  let buffer = []

  for (const rawLine of lines) {
    const line = rawLine.trimEnd()
    const match = line.trim().match(/^###\s+(.*?)\s*$/)
    if (match) {
      if (heading) {
        sections[heading] = buffer.join('\n').trim()
      }
      heading = match[1].trim()
      buffer = []
      continue
    }

    if (heading) {
      buffer.push(line)
    }
  }

  if (heading) {
    sections[heading] = buffer.join('\n').trim()
  }

  const normalized = {}
  for (const [label, key] of Object.entries(FIELD_MAP)) {
    const raw = sections[label] || ''
    normalized[key] = raw === '_No response_' ? '' : raw
  }
  return normalized
}

function shouldExcludeIssue(issue) {
  if (issue.pull_request) return true
  const labels = new Set((issue.labels || []).map(label => label.name))
  if (!labels.has(ISSUE_LABEL)) return true
  return Array.from(EXCLUDED_LABELS).some(label => labels.has(label))
}

function toSubmission(issue) {
  const parsed = parseIssueForm(issue.body)
  const totalScore = parseNumber(parsed.totalScoreRaw)
  const passRate = parsePassRate(parsed.passRateRaw)
  const labels = (issue.labels || []).map(label => label.name)

  return {
    number: issue.number,
    title: issue.title,
    issueUrl: issue.html_url,
    state: issue.state,
    createdAt: issue.created_at,
    updatedAt: issue.updated_at,
    closedAt: issue.closed_at,
    labels,
    agentName: parsed.agentName || 'Unknown Agent',
    agentVersion: parsed.agentVersion || 'unknown',
    benchmarkVariant: parsed.benchmarkVariant || 'Unknown Variant',
    protocolVersion: parsed.protocolVersion || 'unknown',
    runId: parsed.runId || `issue-${issue.number}`,
    totalScore,
    totalScoreText: parsed.totalScoreRaw || 'n/a',
    passRate,
    passRateText: parsed.passRateRaw || 'n/a',
    submissionRepoUrl: parsed.submissionRepoUrl,
    submissionRef: parsed.submissionRef,
    submissionPackageUrl: parsed.submissionPackageUrl,
    scoreSummaryUrl: parsed.scoreSummaryUrl,
    manifestUrl: parsed.manifestUrl,
    runMetaUrl: parsed.runMetaUrl,
    notes: parsed.notes || '',
    searchText: [
      parsed.agentName,
      parsed.agentVersion,
      parsed.benchmarkVariant,
      parsed.protocolVersion,
      parsed.runId
    ]
      .join(' ')
      .toLowerCase()
  }
}

function compareSubmissions(a, b) {
  const scoreA = a.totalScore ?? -1
  const scoreB = b.totalScore ?? -1
  if (scoreA !== scoreB) return scoreB - scoreA

  const passA = a.passRate ?? -1
  const passB = b.passRate ?? -1
  if (passA !== passB) return passB - passA

  return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
}

function renderAgentAvatar(submission, className = 'agent-avatar') {
  if (submission.agentIconUrl) {
    return `<img class="${className}" src="${escapeHtml(submission.agentIconUrl)}" alt="${escapeHtml(submission.agentName)}" loading="lazy" />`
  }

  const initials = submission.agentName
    .split(/\s+/)
    .slice(0, 2)
    .map(part => part[0] || '')
    .join('')
    .toUpperCase()

  return `<span class="${className} agent-avatar-fallback">${escapeHtml(initials || 'AG')}</span>`
}

function getSubmissionLinks(submission) {
  if (submission.isMock) {
    return [
      ['Official Site', submission.agentHomeUrl],
      ['Source', submission.sourceUrl]
    ].filter(([, url], index, entries) => {
      if (!url) return false
      return entries.findIndex(([, candidate]) => candidate === url) === index
    })
  }

  return [
    ['Issue', submission.issueUrl],
    ['Repository', submission.submissionRepoUrl],
    ['Submission Package', submission.submissionPackageUrl],
    ['Score Summary', submission.scoreSummaryUrl],
    ['Manifest', submission.manifestUrl],
    ['Run Metadata', submission.runMetaUrl]
  ].filter(([, url]) => Boolean(url))
}

function renderSubmissionLinks(submission, limit = Infinity) {
  const links = getSubmissionLinks(submission).slice(0, limit)
  if (links.length === 0) return 'n/a'

  return links
    .map(
      ([label, url]) =>
        `<a href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${escapeHtml(label.toLowerCase())}</a>`
    )
    .join(' / ')
}

async function fetchIssues() {
  const issues = []

  for (let page = 1; page <= 10; page += 1) {
    const url = new URL(`${API_BASE}/issues`)
    url.searchParams.set('state', 'all')
    url.searchParams.set('labels', ISSUE_LABEL)
    url.searchParams.set('per_page', '100')
    url.searchParams.set('page', String(page))

    const response = await fetch(url, {
      headers: {
        Accept: 'application/vnd.github+json'
      }
    })

    if (!response.ok) {
      throw new Error(`GitHub API returned ${response.status}`)
    }

    const pageItems = await response.json()
    if (!Array.isArray(pageItems) || pageItems.length === 0) break
    issues.push(...pageItems)

    if (pageItems.length < 100) break
  }

  return issues
}

function updateSummary() {
  const submissions = state.filtered
  const uniqueAgents = new Set(submissions.map(item => item.agentName.toLowerCase()))
  const variants = new Set(submissions.map(item => item.benchmarkVariant))
  const topScore = submissions.length > 0 ? submissions[0].totalScoreText : 'n/a'
  const renderedAt = formatDateTime(new Date().toISOString())

  elements.statSubmissionsLabel.textContent = isMockMode() ? 'Mock Entries' : 'Validated Submissions'
  elements.statSubmissions.textContent = String(submissions.length)
  elements.statAgents.textContent = String(uniqueAgents.size)
  elements.statTopScore.textContent = String(topScore)
  elements.statVariants.textContent = String(variants.size)
  elements.lastUpdated.textContent = isMockMode()
    ? `Preview updated: ${renderedAt}`
    : `Last updated: ${renderedAt}`
  elements.dataSource.textContent = isMockMode()
    ? `Source: ${MOCK_SOURCE_SUMMARY}`
    : `Source: ${API_BASE}/issues?labels=${ISSUE_LABEL}`
}

function renderVariantFilter() {
  const variants = Array.from(new Set(state.submissions.map(item => item.benchmarkVariant))).sort()
  const options = ['<option value="all">All variants</option>']
  for (const variant of variants) {
    const selected = state.variantFilter === variant ? ' selected' : ''
    options.push(`<option value="${escapeHtml(variant)}"${selected}>${escapeHtml(variant)}</option>`)
  }
  elements.variantFilter.innerHTML = options.join('')
}

function applyFilters() {
  const next = state.submissions.filter(item => {
    if (state.variantFilter !== 'all' && item.benchmarkVariant !== state.variantFilter) {
      return false
    }
    return true
  })

  state.filtered = next.sort(compareSubmissions)
  if (!state.filtered.some(item => item.number === state.selectedNumber)) {
    state.selectedNumber = state.filtered[0]?.number ?? null
  }
}

function renderTable() {
  if (state.filtered.length === 0) {
    elements.leaderboardBody.innerHTML = `
      <tr>
        <td colspan="7" class="table-empty">No leaderboard entries found for the current filter.</td>
      </tr>
    `
    return
  }

  const rows = state.filtered.map((submission, index) => {
    const isSelected = submission.number === state.selectedNumber
    const rowClasses = [isSelected ? 'is-selected' : '', submission.isFeatured ? 'is-featured' : '']
      .filter(Boolean)
      .join(' ')

    return `
      <tr data-issue-number="${submission.number}" class="${rowClasses}">
        <td><span class="rank-pill">#${index + 1}</span></td>
        <td>
          <div class="agent-cell">
            ${renderAgentAvatar(submission)}
            <div>
              <strong>${escapeHtml(submission.agentName)}</strong>
              <span class="score-sub">${escapeHtml(submission.agentVersion)}</span>
            </div>
          </div>
        </td>
        <td>${escapeHtml(submission.benchmarkVariant)}</td>
        <td>
          <span class="score-main">${escapeHtml(submission.totalScoreText)}</span>
          <span class="score-sub">protocol ${escapeHtml(submission.protocolVersion)}</span>
        </td>
        <td>${escapeHtml(submission.passRateText)}</td>
        <td>${escapeHtml(formatDate(submission.createdAt))}</td>
        <td>${renderSubmissionLinks(submission, 2)}</td>
      </tr>
    `
  })

  elements.leaderboardBody.innerHTML = rows.join('')

  elements.leaderboardBody.querySelectorAll('tr[data-issue-number]').forEach(row => {
    row.addEventListener('click', () => {
      const issueNumber = Number(row.getAttribute('data-issue-number'))
      state.selectedNumber = issueNumber
      renderTable()
      renderDetail()
    })
  })
}

function renderDetail() {
  const submission = state.filtered.find(item => item.number === state.selectedNumber)
  if (!submission) {
    elements.detailCard.className = 'detail-card detail-empty'
    elements.detailCard.textContent =
      'No leaderboard entries match the current filter.'
    return
  }

  const links = getSubmissionLinks(submission)
    .filter(([, url]) => Boolean(url))
    .map(
      ([label, url]) => `
        <a class="detail-link" href="${escapeHtml(url)}" target="_blank" rel="noreferrer">
          ${escapeHtml(label)}
          <span>${escapeHtml(url)}</span>
        </a>
      `
    )
    .join('')

  const chips = submission.labels
    .map(label => {
      const chipClass =
        label === 'validated' ? 'chip chip-validated' : label === 'featured' ? 'chip chip-featured' : 'chip'
      return `<span class="${chipClass}">${escapeHtml(label)}</span>`
    })
    .join('')

  const notes = submission.notes
    ? `
      <div class="detail-section">
        <h3>Notes</h3>
        <div class="detail-item">${escapeHtml(submission.notes)}</div>
      </div>
    `
    : ''

  const warning = submission.state === 'closed'
    ? '<div class="warning-box">This submission issue is closed. It remains visible because the validated metadata is still public.</div>'
    : submission.isFeatured
      ? '<div class="warning-box">Featured reference project for this benchmark site.</div>'
    : submission.isMock
      ? `<div class="warning-box">Mock preview entry seeded from official branding. Source: ${escapeHtml(submission.sourceTitle || 'official product page')}.</div>`
      : ''
  const linksHeading = submission.isMock ? 'Product Links' : 'Evidence Links'

  elements.detailCard.className = 'detail-card'
  elements.detailCard.innerHTML = `
    <div class="chip-row">${chips}</div>
    <div class="detail-identity">
      ${renderAgentAvatar(submission, 'agent-avatar agent-avatar-detail')}
      <div>
        <h3 class="detail-title">${escapeHtml(submission.agentName)}</h3>
        <p class="detail-subtitle">
          ${escapeHtml(submission.agentVersion)} · ${escapeHtml(submission.benchmarkVariant)} · run ${escapeHtml(submission.runId)}
        </p>
      </div>
    </div>

    <div class="detail-meta">Submitted ${escapeHtml(formatDateTime(submission.createdAt))}</div>

    <div class="detail-section">
      <h3>Score Envelope</h3>
      <div class="detail-grid">
        <div class="detail-item">
          <strong>Total Score</strong>
          ${escapeHtml(submission.totalScoreText)}
        </div>
        <div class="detail-item">
          <strong>Pass Rate</strong>
          ${escapeHtml(submission.passRateText)}
        </div>
        <div class="detail-item">
          <strong>Protocol Version</strong>
          ${escapeHtml(submission.protocolVersion)}
        </div>
        <div class="detail-item">
          <strong>Submission Ref</strong>
          ${escapeHtml(submission.submissionRef || 'n/a')}
        </div>
      </div>
    </div>

    <div class="detail-section">
      <h3>${escapeHtml(linksHeading)}</h3>
      <div class="detail-links">${links || '<div class="detail-item">No public links provided.</div>'}</div>
    </div>

    ${notes}
    ${warning}
  `
}

async function loadLeaderboard() {
  elements.refreshButton.disabled = true
  setTerminal([
    '$ fetch validated submissions',
    `repo=${REPO_OWNER}/${REPO_NAME}`,
    `skill=main/SKILL.md`,
    'submit=benchmark-submission.yml',
    `labels=${ISSUE_LABEL}`,
    'status=connecting'
  ])

  try {
    const issues = await fetchIssues()
    const filteredIssues = issues.filter(issue => !shouldExcludeIssue(issue))
    state.dataMode = filteredIssues.length > 0 ? DATA_MODE.LIVE : DATA_MODE.MOCK
    state.submissions = (filteredIssues.length > 0 ? filteredIssues.map(toSubmission) : MOCK_SUBMISSIONS).sort(
      compareSubmissions
    )
    renderVariantFilter()
    applyFilters()
    updateSummary()
    renderTable()
    renderDetail()

    setTerminal([
      '$ fetch validated submissions',
      `repo=${REPO_OWNER}/${REPO_NAME}`,
      `skill=main/SKILL.md`,
      `issues_total=${issues.length}`,
      `issues_rendered=${state.submissions.length}`,
      `mode=${state.dataMode}`,
      'status=ok'
    ])
  } catch (error) {
    console.error('[Leaderboard] failed to load submissions', error)
    state.dataMode = DATA_MODE.LIVE
    state.submissions = []
    state.filtered = []
    updateSummary()
    renderTable()
    renderDetail()

    setTerminal([
      '$ fetch validated submissions',
      `repo=${REPO_OWNER}/${REPO_NAME}`,
      `skill=main/SKILL.md`,
      `status=error`,
      String(error instanceof Error ? error.message : error)
    ])
  } finally {
    elements.refreshButton.disabled = false
  }
}

elements.refreshButton.addEventListener('click', () => {
  void loadLeaderboard()
})

elements.copyCommandButton.addEventListener('click', () => {
  void copyAgentPrompt()
})

elements.variantFilter.addEventListener('change', event => {
  state.variantFilter = event.target.value
  applyFilters()
  updateSummary()
  renderTable()
  renderDetail()
})

renderAgentPrompt()
void loadLeaderboard()
