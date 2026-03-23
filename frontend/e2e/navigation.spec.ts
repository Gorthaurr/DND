import { test, expect } from '@playwright/test';

const SCREENSHOTS_DIR = 'e2e/screenshots';

test.describe('Navigation between pages', () => {
  test('navigate from main to character and back', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${SCREENSHOTS_DIR}/nav-start-main.png` });

    await page.goto('/character');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${SCREENSHOTS_DIR}/nav-to-character.png` });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${SCREENSHOTS_DIR}/nav-back-to-main.png` });
  });

  test('navigate to worldbuilder', async ({ page }) => {
    await page.goto('/worldbuilder');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${SCREENSHOTS_DIR}/nav-worldbuilder.png` });
    await expect(page).toHaveURL(/worldbuilder/);
  });

  test('404 page for unknown route', async ({ page }) => {
    await page.goto('/nonexistent-page');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: `${SCREENSHOTS_DIR}/nav-404.png` });
  });
});
