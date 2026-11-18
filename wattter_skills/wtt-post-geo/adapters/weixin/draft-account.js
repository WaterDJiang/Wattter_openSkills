import { CliError } from '@jackwener/opencli/errors';
import { cli, Strategy } from '@jackwener/opencli/registry';
import { accountResult, assertHttp, getCookieHeader, request } from '../_wtt_post/shared.js';

const HOME_URL = 'https://mp.weixin.qq.com/';

cli({
  site: 'weixin',
  name: 'draft-account',
  description: '检查公众号 Cookie 草稿 adapter 的当前登录账号',
  access: 'read',
  domain: 'mp.weixin.qq.com',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [],
  columns: ['status', 'platform', 'account', 'account_id'],
  func: async (page) => {
    const cookie = await getCookieHeader(page, [HOME_URL]);
    const result = await request(HOME_URL, {
      headers: {
        Cookie: cookie,
        Origin: 'https://mp.weixin.qq.com',
        Referer: 'https://mp.weixin.qq.com/',
      },
    });
    assertHttp(result.response, result.text, '检查公众号登录账号');
    const home = result.text;
    const token = home.match(/t:\s*["']([^"']+)["']\s*\|\|/)?.[1];
    if (!token) throw new CliError('AUTH_REQUIRED', '未识别到公众号 token，请先登录 mp.weixin.qq.com');
    const account =
      home.match(/nick_name\s*=\s*["']([^"']+)["']/)?.[1] ||
      home.match(/user_name\s*=\s*["']([^"']+)["']/)?.[1] ||
      '公众号账号';
    const accountId = home.match(/user_name\s*=\s*["']([^"']+)["']/)?.[1] || token;
    return accountResult({ platform: 'weixin', account, accountId });
  },
});
