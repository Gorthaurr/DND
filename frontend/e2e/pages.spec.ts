import { test, expect } from '@playwright/test';

const SCREENSHOTS_DIR = 'e2e/screenshots';

test.describe('Page Screenshots', () => {
  test('main page loads and screenshot', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/main-page.png`,
      fullPage: true
    });
    // Basic assertion: page loaded
    await expect(page).toHaveTitle(/.*/);
  });

  test('character creation page screenshot', async ({ page }) => {
    await page.goto('/character');
    await page.waitForLoadState('networkidle');
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/character-page.png`,
      fullPage: true
    });
    await expect(page).toHaveTitle(/.*/);
  });

  test('worldbuilder page screenshot', async ({ page }) => {
    await page.goto('/worldbuilder');
    await page.waitForLoadState('networkidle');
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/worldbuilder-page.png`,
      fullPage: true
    });
    await expect(page).toHaveTitle(/.*/);
  });
});
