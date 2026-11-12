import { renderAgentMarkdown } from 'app/modules/ai-agent/agent-markdown';
import { ChatCitationViewModel } from 'app/modules/ai-agent/viewmodels/chat-message.viewmodel';

const citations: ChatCitationViewModel[] = [
  { articleId: 1, code: 'CB024', title: 'Kidney damage markers', year: 2018, sourceUrl: 'https://doi.org/10.1/x' },
  { articleId: 2, code: 'CB040', title: '320 cases', year: 2019, sourceUrl: null },
];

describe('renderAgentMarkdown', () => {
  it('escapes HTML in the model text', () => {
    const html = renderAgentMarkdown('<script>alert(1)</script> & "quotes"');
    expect(html).toBe('<p>&lt;script&gt;alert(1)&lt;/script&gt; &amp; &quot;quotes&quot;</p>');
  });

  it('links a resolved citation to its source and keeps the section label', () => {
    const html = renderAgentMarkdown('Azotaemia was common [CB024 Results].', citations);
    expect(html).toContain('<span class="agent-cite">[<a href="https://doi.org/10.1/x" target="_blank" rel="noopener noreferrer" title="Kidney damage markers (2018)">CB024</a> Results]</span>');
  });

  it('marks a citation with no link as an abbreviation, and leaves unknown codes as text', () => {
    const html = renderAgentMarkdown('See [CB040, CB999].', citations);
    expect(html).toContain('<abbr title="320 cases (2019)">CB040</abbr>, CB999]');
  });

  it('links a cited experiment and clinical page to their screens, by code or by alias', () => {
    const appLinks = [
      { code: 'SV-05-01-age-death', aliases: ['SV-05-01'], href: 'experiments/SV-05-01-age-death', title: 'Age and death' },
      { code: 'SY05', href: 'clinical/SY05', title: 'Acute kidney injury' },
    ];
    const html = renderAgentMarkdown('No effect [SV-05-01-age-death]; see [SV-05-01] and [SY05, CB024].', citations, { appLinks });
    expect(html).toContain('[<a href="experiments/SV-05-01-age-death" target="_blank" rel="noopener" title="Age and death">SV-05-01-age-death</a>]');
    expect(html).toContain('[<a href="experiments/SV-05-01-age-death" target="_blank" rel="noopener" title="Age and death">SV-05-01</a>]');
    expect(html).toContain('[<a href="clinical/SY05" target="_blank" rel="noopener" title="Acute kidney injury">SY05</a>, <a href="https://doi.org/10.1/x"');
  });

  it('leaves an app code the server did not resolve, a dataset code and a plain bracket as text', () => {
    const html = renderAgentMarkdown('See [SY07], [S-CB040] and [sic].', citations);
    expect(html).toBe('<p>See [SY07], [S-CB040] and [sic].</p>');
  });

  it('renders lists, headings, emphasis and code', () => {
    const html = renderAgentMarkdown('## Findings\n\n- **Anaemia** in *most* dogs\n- `PCV` < 15%\n\n1. one\n2. two');
    expect(html).toBe(
      '<h4>Findings</h4>'
      + '<ul><li><strong>Anaemia</strong> in <em>most</em> dogs</li><li><code>PCV</code> &lt; 15%</li></ul>'
      + '<ol><li>one</li><li>two</li></ol>');
  });

  it('renders a table with a header row', () => {
    const html = renderAgentMarkdown('| Marker | Article |\n|---|:-:|\n| uNGAL | [CB024] |');
    expect(html).toContain('<thead><tr><th>Marker</th><th>Article</th></tr></thead>');
    expect(html).toContain('<td>uNGAL</td>');
  });

  it('only links http(s) URLs', () => {
    expect(renderAgentMarkdown('[x](javascript:alert(1))')).not.toContain('<a');
    expect(renderAgentMarkdown('[PubMed](https://pubmed.ncbi.nlm.nih.gov/1/)')).toContain('<a href="https://pubmed.ncbi.nlm.nih.gov/1/"');
  });

  it('does not italicise snake_case or B. rossi style text', () => {
    expect(renderAgentMarkdown('article_section and 2 * 3 * 4')).toBe('<p>article_section and 2 * 3 * 4</p>');
  });
});
