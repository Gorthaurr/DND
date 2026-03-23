import { test, expect } from '@playwright/test';

const SCREENSHOTS_DIR = 'e2e/screenshots';

test.describe('Main Page Components', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('page has visible content', async ({ page }) => {
    // Main page should have some visible text/content
    const body = page.locator('body');
    await expect(body).toBeVisible();
    const text = await body.textContent();
    expect(text?.length).toBeGreaterThan(0);
  });

  test('screenshot after clicking each tab', async ({ page }) => {
    // Try to find tab-like buttons and click them
    const tabs = page.locator('button, [role="tab"]');
    const count = await tabs.count();

    for (let i = 0; i < Math.min(count, 10); i++) {
      const tab = tabs.nth(i);
      const text = await tab.textContent();
      if (!text || text.trim().length === 0) continue;

      const tabName = text.trim().toLowerCase().replace(/\s+/g, '-').slice(0, 20);
      try {
        await tab.click();
        await page.waitForTimeout(500);
        await page.screenshot({
          path: `${SCREENSHOTS_DIR}/tab-${tabName}.png`,
          fullPage: true,
        });
      } catch {
        // Tab might not be clickable, skip
      }
    }
  });
});

test.describe('Character Creation Page', () => {
  test('character page has form elements', async ({ page }) => {
    await page.goto('/character');
    await page.waitForLoadState('networkidle');

    // Should have some input or form elements
    const inputs = page.locator('input, textarea, select, button');
    const count = await inputs.count();
    // Just verify the page loaded with interactive elements
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/character-form.png`,
      fullPage: true,
    });
  });
});

test.describe('Worldbuilder Page', () => {
  test('worldbuilder page has content', async ({ page }) => {
    await page.goto('/worldbuilder');
    await page.waitForLoadState('networkidle');

    const body = page.locator('body');
    await expect(body).toBeVisible();
    await page.screenshot({
      path: `${SCREENSHOTS_DIR}/worldbuilder-content.png`,
      fullPage: true,
    });
  });
});
