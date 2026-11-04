import { PermissionsViewModel } from 'app/core/viewmodels/permissions.viewmodel';
import {
  NO_PERMISSION_HINT,
  NO_PERMISSION_TOOLTIP,
  PERMISSION_KEYS,
  PERMISSION_KEY_LIST,
  hasPermission,
  isPermissionKey,
  permissionHint,
  permissionTooltip,
} from 'app/core/permissions/permission-keys';

/**
 * The registry is a contract with the C# controllers, so the assertions here
 * are about the *shape* of that contract — nothing catches a key that drifted
 * away from its controller except reading the controller, which is why the
 * module documents that obligation.
 */
describe('permission keys', () => {

  it('emits a distinct wire key per capability', () => {
    const unique = new Set<string>(PERMISSION_KEY_LIST);

    expect(unique.size).toBe(PERMISSION_KEY_LIST.length);
  });

  it('spells every key camelCase beginning with "can"', () => {
    const malformed = PERMISSION_KEY_LIST.filter(key => !/^can[A-Z][A-Za-z]*$/.test(key));

    expect(malformed).toEqual([]);
  });

  it('recognises its own keys and rejects a typo', () => {
    expect(isPermissionKey(PERMISSION_KEYS.edit)).toBeTrue();
    expect(isPermissionKey('canEddit')).toBeFalse();
  });
});

describe('hasPermission', () => {

  it('reads a granted capability off the echo', () => {
    const permissions = new PermissionsViewModel({ canEdit: true });

    expect(hasPermission(permissions, PERMISSION_KEYS.edit)).toBeTrue();
  });

  it('denies a capability the echo set false', () => {
    const permissions = new PermissionsViewModel({ canEdit: false });

    expect(hasPermission(permissions, PERMISSION_KEYS.edit)).toBeFalse();
  });

  // The window between navigation and the first response: no echo has arrived,
  // and an action must not be enabled on the assumption that one will.
  it('denies everything while the screen has no echo', () => {
    expect(hasPermission(undefined, PERMISSION_KEYS.read)).toBeFalse();
    expect(hasPermission(null, PERMISSION_KEYS.read)).toBeFalse();
  });
});

describe('denial affordances', () => {

  it('keeps the label when permitted and explains the denial when not', () => {
    expect(permissionTooltip(true, 'Deploy')).toBe('Deploy');
    expect(permissionTooltip(false, 'Deploy')).toBe(NO_PERMISSION_TOOLTIP);
  });

  // `undefined` rather than '' so the hint can be spread onto a grid menu item
  // without rendering an empty one.
  it('hints only on a denied menu item', () => {
    expect(permissionHint(true)).toBeUndefined();
    expect(permissionHint(false)).toBe(NO_PERMISSION_HINT);
  });
});
