import { CliError } from '@jackwener/opencli/errors';
import { cli, Strategy } from '@jackwener/opencli/registry';
import { accountResult, assertHttp, getCookieHeader, request } from '../_wtt_post/shared.js';

cli({
  site: 'cnblogs',
  name: 'draft-account',
  description: '检查博客园草稿 adapter 的当前登录账号',
  access: 'read',
  domain: 'home.cnblogs.com',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [],
  columns: ['status', 'platform', 'account', 'account_id'],
  func: async (page) => {
    const cookie = await getCookieHeader(page, ['https://home.cnblogs.com/', 'https://i.cnblogs.com/', 'https://www.cnblogs.com/']);
    const result = await request('https://home.cnblogs.com/user/CurrentUserInfo', {
      headers: { Cookie: cookie, Referer: 'https://home.cnblogs.com/', 'X-Requested-With': 'XMLHttpRequest' },
    });
    assertHttp(result.response, result.text, '检查博客园登录账号');
    const username = result.text.match(/href="\/u\/([^/]+)\//)?.[1];
    const displayName = result.text.match(/href="\/u\/[^/]+\/"[^>]*>([^<]*)<\/a>/)?.[1]?.trim();
    if (!username) throw new CliError('AUTH_REQUIRED', '未识别到博客园登录账号');
    return accountResult({ platform: 'cnblogs', account: displayName || username, accountId: username });
  },
});
