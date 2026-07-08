import contacts from '../../../cypress/fixtures/addressbook/contacts.json';
import resources from '../../../cypress/fixtures/resources/resources.json';
import { expect, test } from '../../fixtures';
import { authFile } from '../../helpers/users';

const currentResource = resources[1];

test.use({ storageState: authFile('collectivité1') });

test.describe(
  'I can see the resource contact list if im logged',
  { tag: '@acces-ressources' },
  () => {
    test('see the contact list', async ({ page }) => {
      await page.goto(`/ressource/${currentResource.pk}/`);

      await expect(
        page.getByText(contacts[1].fields.first_name!).first()
      ).toBeVisible();
      await expect(
        page.getByText(contacts[2].fields.first_name!).first()
      ).toBeVisible();
      await expect(
        page.getByText(contacts[3].fields.first_name!).first()
      ).toBeVisible();
    });
  }
);
