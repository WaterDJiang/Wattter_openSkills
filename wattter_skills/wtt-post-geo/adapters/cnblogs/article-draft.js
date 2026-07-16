import { CliError } from '@jackwener/opencli/errors';
import { cli, Strategy } from '@jackwener/opencli/registry';
import {
  assertHttp,
  assertNoLocalImages,
  draftResult,
  getCookieHeader,
  parseCsv,
  parseJson,
  readPayloadFile,
  request,
  requireExecute,
} from '../_wtt_post/shared.js';

cli({
  site: 'cnblogs',
  name: 'article-draft',
  access: 'write',
  description: '使用浏览器登录态创建博客园文章草稿（无 CSDN 插件）',
  domain: 'i.cnblogs.com',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [
    { name: 'title', required: true, help: '文章标题' },
    { name: 'file', required: true, help: '已适配的 UTF-8 Markdown 文件' },
    { name: 'summary', help: '文章摘要' },
    { name: 'tags', help: '逗号分隔的标签' },
    { name: 'execute', type: 'boolean', help: '确认创建草稿' },
  ],
  columns: ['status', 'write_state', 'provider', 'platform', 'account', 'draft_id', 'draft_url', 'detail'],
  func: async (page, kwargs) => {
    requireExecute(kwargs);
    const title = String(kwargs.title || '').trim();
    if (!title) throw new CliError('INVALID_INPUT', '--title is required');
    const markdown = await readPayloadFile(kwargs.file);
    assertNoLocalImages(markdown);
    const cookie = await getCookieHeader(page, ['https://i.cnblogs.com/', 'https://home.cnblogs.com/', 'https://www.cnblogs.com/']);
    const xsrfCookie = cookie.split('; ').find((part) => part.startsWith('XSRF-TOKEN='));
    const xsrf = xsrfCookie ? decodeURIComponent(xsrfCookie.slice('XSRF-TOKEN='.length)) : '';
    if (!xsrf) throw new CliError('AUTH_REQUIRED', '博客园 XSRF-TOKEN 缺失，请刷新文章后台');

    const meResponse = await request('https://home.cnblogs.com/user/CurrentUserInfo', {
      headers: { Cookie: cookie, Referer: 'https://home.cnblogs.com/', 'X-Requested-With': 'XMLHttpRequest' },
    });
    assertHttp(meResponse.response, meResponse.text, '检查博客园登录态');
    const username = meResponse.text.match(/href="\/u\/([^/]+)\//)?.[1];
    if (!username) throw new CliError('AUTH_REQUIRED', '未识别到博客园登录账号');

    const createdResponse = await request('https://i.cnblogs.com/api/posts', {
      method: 'POST',
      headers: {
        Cookie: cookie,
        Origin: 'https://i.cnblogs.com',
        Referer: 'https://i.cnblogs.com/posts/edit',
        'Content-Type': 'application/json',
        'x-xsrf-token': xsrf,
      },
      body: JSON.stringify({
        id: null, postType: 2, accessPermission: 0, title, url: null,
        postBody: markdown, categoryIds: [], categories: null, collectionIds: [],
        inSiteCandidate: false, inSiteHome: false, siteCategoryId: null, blogTeamIds: null,
        isPublished: false, displayOnHomePage: false, isAllowComments: true,
        includeInMainSyndication: false, isPinned: false, showBodyWhenPinned: false,
        isOnlyForRegisterUser: false, isUpdateDateAdded: false, entryName: null,
        description: String(kwargs.summary || '') || null, featuredImage: null,
        tags: parseCsv(kwargs.tags), password: null, publishAt: null,
        datePublished: new Date().toISOString(), dateUpdated: null, isMarkdown: true,
        isDraft: false, autoDesc: null, changePostType: false, blogId: 0,
        author: null, removeScript: false, clientInfo: null, changeCreatedTime: false,
        canChangeCreatedTime: false, isContributeToImpressiveBugActivity: false,
        usingEditorId: 5, sourceUrl: null,
      }),
    });
    assertHttp(createdResponse.response, createdResponse.text, '创建博客园草稿');
    const created = parseJson(createdResponse.text, '创建博客园草稿');
    if (!created.id) throw new CliError('API_ERROR', created.error || created.message || '博客园草稿响应缺少 ID');
    return draftResult({
      platform: 'cnblogs',
      account: username,
      draftId: created.id,
      draftUrl: `https://i.cnblogs.com/articles/edit;postId=${created.id}`,
    });
  },
});

