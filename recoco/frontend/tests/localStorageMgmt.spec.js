/**
 * @jest-environment jsdom
 */
import { LocalStorageMgmt } from '../src/js/utils/localStorageMgmt';

describe('LocalStorageMgmt', () => {
  let instance;
  beforeEach(() => {
    instance = new LocalStorageMgmt({
      dataLabel: 'test-data',
      tag: 'test-tag',
      expiringData: false,
    });
  });

  afterEach(() => {
    localStorage.removeItem('test-data-test-tag');
  });

  it('should set data in local storage', () => {
    instance.set({ test: 'data' });
    const data = JSON.parse(localStorage.getItem('test-data-test-tag'));
    expect(data.data).toEqual({ test: 'data' });
  });

  it('should get data from local storage', () => {
    localStorage.setItem(
      'test-data-test-tag',
      JSON.stringify({ data: { test: 'data' }, version: instance.version })
    );
    const data = instance.get();
    expect(data).toEqual({ test: 'data' });
  });

  it('should not get data from local storage when version is incorrect', () => {
    localStorage.setItem(
      'test-data-test-tag',
      JSON.stringify({ data: { test: 'data' }, version: '0.0.1' })
    );
    const data = instance.get();
    expect(data).toBeNull();
  });

  it('should not get data from local storage when time is expired', () => {
    instance.expiringData = true;

    localStorage.setItem(
      'test-data-test-tag',
      JSON.stringify({
        data: { test: 'data' },
        version: instance.version,
        expireAt: new Date(),
      })
    );
    const data = instance.get();
    expect(data).toBeNull();
  });

  it('should reset data from local storage', () => {
    instance.set({ test: 'data' });
    localStorage.setItem(
      'test-data-test-tag',
      JSON.stringify({
        data: { test: 'data' },
        version: instance.version,
      })
    );
    instance.reset();
    const data = localStorage.getItem('test-data-test-tag');
    expect(data).toBeNull();
  });
});
