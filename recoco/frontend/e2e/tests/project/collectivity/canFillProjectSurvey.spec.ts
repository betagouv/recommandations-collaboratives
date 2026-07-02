import file from '../../../../cypress/fixtures/documents/file.json';
import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.describe(
  'I can fill a project survey',
  { tag: ['@critical', '@page-projet-edl'] },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test.skip('displays the tutorial on a pristine survey', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/connaissance`);

      await page
        .locator('[data-test-id="link-fill-survey"]')
        .first()
        .click({ force: true });

      await expect(
        page.locator("[data-test-id='survey-tutorial']")
      ).toBeAttached();
    });

    test('fills up the survey and upload a file', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/connaissance`);

      await page
        .locator('[data-test-id="link-fill-survey-cta"]')
        .first()
        .click({ force: true });

      await page.locator('#form_answer-1').check({ force: true });

      const comment = page.locator('#input-project-comment');
      await comment.fill('Fake comment on first survey question');
      await expect(comment).toHaveValue('Fake comment on first survey question');

      await page.locator('[name="attachment"]').setInputFiles(file.path);

      await page
        .locator('[data-test-id="button-submit-survey-questionset"]')
        .click({ force: true });

      await page.locator('#form_answer-1').check({ force: true });

      const comment2 = page.locator('#input-project-comment');
      await comment2.fill('Fake comment on first survey question');
      await expect(comment2).toHaveValue(
        'Fake comment on first survey question'
      );

      await page
        .locator('[data-test-id="button-submit-survey-questionset"]')
        .click({ force: true });

      await page
        .locator('[data-test-id="project-navigation-knowledge"]')
        .click({ force: true });
      await expect(page).toHaveURL(/\/connaissance/);
      await expect(page.getByText('Propriété du site').first()).toBeVisible();
      await expect(page.getByText('100%').first()).toBeVisible();
      await expect(
        page.getByText('Fake comment on first survey question').first()
      ).toBeVisible();

      // Reload the survey: it should not load tutorial
      await page.locator('[data-cy="edit-survey"]').first().click();
      await expect(
        page.locator('[data-test-id="survey-tutorial"]')
      ).toHaveCount(0);
    });

    test('can see and download the file', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/documents`);

      await expect(
        page.getByText("Fichier récupéré de l'état des lieux").first()
      ).toBeVisible();

      // test download with playwright verification
      const filename = (
        await page.locator('[data-cy="attachment-filename"]').first().innerText()
      ).trim();
      const downloadPromise = page.waitForEvent('download');
      await page.locator('[data-test-id="download-attachment"]').click();
      const download = await downloadPromise;
      expect(await download.path()).toBeTruthy();
      expect(filename.length).toBeGreaterThan(0);
    });
  }
);
