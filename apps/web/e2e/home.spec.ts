import {test,expect} from '@playwright/test';
test('accueil et preuve visuelle',async ({page})=>{await page.goto('/');await expect(page.getByRole('heading',{name:'Agentic Dev Foundation'})).toBeVisible();await page.screenshot({path:'test-results/home.png',fullPage:true});});
