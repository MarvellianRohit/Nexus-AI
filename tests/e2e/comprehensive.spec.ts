
import { test, expect, chromium, Browser, Page } from '@playwright/test';

test.describe('Nexus AI - Comprehensive E2E Suite', () => {


    test('Home Page: should load successfully', async ({ page }) => {
        await page.goto('/');
        await expect(page.getByText(/Hide Preview/i)).toBeVisible();
    });

    test('Studio Page: should load successfully', async ({ page }) => {
        await page.goto('/studio');
        await expect(page.getByText(/How would you like to build today/i)).toBeVisible();
    });

    test('Settings Page: should load successfully', async ({ page }) => {
        await page.goto('/settings');
        await expect(page.getByRole('heading', { name: /Settings/i })).toBeVisible();
    });

    test('Dashboard Page: should load successfully', async ({ page }) => {
        await page.goto('/dashboard');
        await expect(page.getByRole('heading', { name: /Dashboard/i })).toBeVisible();
    });

    test('Community Page: should load successfully', async ({ page }) => {
        await page.goto('/community');
        await expect(page.getByRole('heading', { name: /Prompt Library/i })).toBeVisible();
    });

    test('Login Page: should load successfully', async ({ page }) => {
        await page.goto('/login');
        await expect(page.getByRole('heading', { name: /Welcome Back/i })).toBeVisible();
    });

    test('Billing Page: should load successfully', async ({ page }) => {
        await page.goto('/billing');
        await expect(page.getByRole('heading', { name: /Simple, Transparent Pricing/i })).toBeVisible();
    });

    test('Generation Page: should load successfully', async ({ page }) => {
        await page.goto('/generation');
        await expect(page.getByRole('heading', { name: /Image Generation/i })).toBeVisible();
    });

    test('Analytics Page: should load successfully', async ({ page }) => {
        await page.goto('/analytics');
        await expect(page.getByRole('heading', { name: /Analytics Dashboard/i })).toBeVisible();
    });

    test('Team Page: should load successfully', async ({ page }) => {
        await page.goto('/team');
        await expect(page.getByRole('heading', { name: /Team Management/i })).toBeVisible();
    });

    test('Knowledge Page: should load successfully', async ({ page }) => {
        await page.goto('/knowledge');
        await expect(page.getByRole('heading', { name: /Knowledge Base/i })).toBeVisible();
    });
});
