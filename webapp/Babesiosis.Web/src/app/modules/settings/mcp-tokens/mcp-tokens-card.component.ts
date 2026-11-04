import {
  ChangeDetectionStrategy,
  Component,
  computed,
  DestroyRef,
  inject,
  OnInit,
  signal,
  TemplateRef,
  ViewChild,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import {
  FsBadgeComponent,
  FsBannerComponent,
  FsButtonComponent,
  FsCardComponent,
  FsConfirmDialogComponent,
  FsDataGridComponent,
  FsFormFieldComponent,
  FsGridCellContext,
  FsGridColumn,
  FsGridPager,
  FsGridSearchPanel,
  FsGridSorting,
  FsGridToolbar,
  FsModalComponent,
  FsSelectComponent,
  FsSelectOption,
  FsSymbolComponent,
  FsTextareaComponent,
  FsTextInputComponent,
  FsToastService,
  writeToClipboard,
} from '@core';
import { ActionItemCommand } from 'app/core/commands/action-item.command';
import { PERMISSION_KEYS, PermissionKey } from 'app/core/permissions/permission-keys';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { PermissionsViewModel } from 'app/core/viewmodels/permissions.viewmodel';
import { SettingsService } from 'app/modules/settings/settings.service';
import {
  PersonalAccessTokenStatus,
  PersonalAccessTokenViewModel,
} from 'app/modules/settings/viewmodels/personal-access-token.viewmodel';

type ExpiryDays = 7 | 30 | 90;

/** Shown in the pasted command wherever the real value is never known to the browser. */
const FUNCTIONS_KEY_PLACEHOLDER = '<functions-key>';
const MCP_URL_PLACEHOLDER = '<mcp-server-url>';
/** The setup instructions (§3.13) never hold a secret: the token is a placeholder too. */
const TOKEN_PLACEHOLDER = '<your-token>';
/**
 * Name the server is registered under in Claude Code (command and config-file examples). One server
 * serves every module (platform/mcp-server.md §3.1, §3.13), so the key is the product's, not a module's.
 */
const MCP_SERVER_NAME = 'babesiosis';

/**
 * Account Settings card "MCP Access Tokens" (platform/mcp-server.md §3.13): the signed-in
 * user's own personal access tokens, Generate (gated on MCP Access), a one-time reveal of the
 * secret with a ready-to-paste `claude mcp add` command, and Revoke on each Active token.
 */
@Component({
  selector: 'fs-mcp-tokens-card',
  templateUrl: './mcp-tokens-card.component.html',
  styleUrls: ['./mcp-tokens-card.component.scss'],
  standalone: true,
  imports: [
    FormsModule,
    FsBadgeComponent,
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsConfirmDialogComponent,
    FsDataGridComponent,
    FsFormFieldComponent,
    FsModalComponent,
    FsSelectComponent,
    FsSymbolComponent,
    FsTextareaComponent,
    FsTextInputComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class McpTokensCardComponent implements OnInit {
  private readonly settingsService = inject(SettingsService);
  private readonly config = inject(ConfigurationService);
  private readonly toast = inject(FsToastService);
  private readonly destroyRef = inject(DestroyRef);

  @ViewChild('statusTpl', { static: true })
  statusTpl!: TemplateRef<FsGridCellContext<PersonalAccessTokenViewModel>>;
  @ViewChild('actionsTpl', { static: true })
  actionsTpl!: TemplateRef<FsGridCellContext<PersonalAccessTokenViewModel>>;

  protected readonly keys = PERMISSION_KEYS;
  protected readonly rows = signal<PersonalAccessTokenViewModel[]>([]);
  protected readonly loading = signal(false);
  protected readonly loadError = signal<string | null>(null);
  protected readonly permissions = signal<PermissionsViewModel | null>(null);

  // Generate dialog
  protected readonly generateOpen = signal(false);
  protected readonly generating = signal(false);
  protected readonly generateError = signal<string | null>(null);
  protected readonly draftName = signal('');
  protected readonly draftExpiry = signal<ExpiryDays>(30);
  protected readonly nameTouched = signal(false);
  protected readonly expiryOptions: FsSelectOption[] = [
    { value: 7, label: '7 Days' },
    { value: 30, label: '30 Days' },
    { value: 90, label: '90 Days' },
  ];
  protected readonly nameError = computed(() => {
    if (!this.nameTouched()) return null;
    const name = this.draftName().trim();
    if (!name) return 'Name is required';
    if (name.length > 100) return 'Name must be at most 100 characters';
    return null;
  });

  // One-time reveal: the secret lives only in this signal and is dropped on close.
  protected readonly revealedSecret = signal<string | null>(null);
  protected readonly revealedName = signal('');
  protected readonly isHosted = !this.config.isLocal;
  protected readonly hasMcpUrl = !!this.config.mcpServerUrl;
  private readonly mcpUrl = this.config.mcpServerUrl || MCP_URL_PLACEHOLDER;
  protected readonly claudeCommand = computed(() => {
    const secret = this.revealedSecret();
    return secret ? this.buildClaudeCommand(secret) : '';
  });

  // Setup instructions (§3.13): visible to every signed-in user, placeholders only, collapsed by default.
  protected readonly helpOpen = signal(false);
  protected readonly serverName = MCP_SERVER_NAME;
  // The instructions always show the functions-key header, labelled hosted-only (§3.13 v1.2).
  protected readonly helpCommand = this.buildClaudeCommand(TOKEN_PLACEHOLDER, true);
  protected readonly helpJson = JSON.stringify({
    mcpServers: {
      [MCP_SERVER_NAME]: {
        type: 'http',
        url: this.mcpUrl,
        headers: {
          Authorization: `Bearer ${TOKEN_PLACEHOLDER}`,
          'x-functions-key': FUNCTIONS_KEY_PLACEHOLDER,
        },
      },
    },
  }, null, 2);

  // Revoke
  protected readonly pendingRevoke = signal<PersonalAccessTokenViewModel | null>(null);
  protected readonly revoking = signal(false);

  protected readonly columns = computed<FsGridColumn<PersonalAccessTokenViewModel>[]>(() => [
    { dataField: 'name', caption: 'Name', minWidth: 140, allowHeaderFiltering: false },
    { dataField: 'prefix', caption: 'Prefix', width: 130, allowHeaderFiltering: false },
    {
      dataField: 'createdDate', caption: 'Created', dataType: 'datetime', width: 165,
      format: v => formatTimestamp(v), allowHeaderFiltering: false, sortOrder: 'desc', sortIndex: 0,
    },
    {
      dataField: 'expiresAt', caption: 'Expires', dataType: 'datetime', width: 165,
      format: v => formatTimestamp(v), allowHeaderFiltering: false,
    },
    {
      dataField: 'lastUsedAt', caption: 'Last Used', dataType: 'datetime', width: 165,
      format: v => formatTimestamp(v, 'Never'), allowHeaderFiltering: false,
    },
    { dataField: 'status', caption: 'Status', width: 100, cellTemplate: this.statusTpl },
    {
      name: 'actions', caption: '', width: 72, alignment: 'center',
      fixed: true, fixedPosition: 'right', cellTemplate: this.actionsTpl,
      allowSorting: false, allowFiltering: false, allowHeaderFiltering: false,
      allowSearch: false, allowHiding: false, allowResizing: false, allowReordering: false,
      showInColumnChooser: false,
    },
  ]);

  protected readonly sorting: FsGridSorting = { mode: 'single' };
  protected readonly searchPanel: FsGridSearchPanel = { visible: true, width: 200, placeholder: 'Search tokens…' };
  protected readonly pager: FsGridPager = { visible: true, showInfo: true, showNavigationButtons: true };
  protected readonly toolbar = computed<FsGridToolbar>(() => ({
    visible: true,
    items: [
      { name: 'searchPanel', location: 'before' },
      {
        name: 'refresh', location: 'after', icon: 'refresh', text: 'Refresh', showText: 'always',
        disabled: this.loading(), onClick: () => this.load(),
      },
    ],
  }));

  ngOnInit(): void {
    this.load();
  }

  protected can(key: PermissionKey): boolean {
    return this.permissions()?.has(key) ?? false;
  }

  protected canRevokeRow(row: PersonalAccessTokenViewModel): boolean {
    return this.can(this.keys.revoke) && row.status === 'Active';
  }

  protected statusIntent(status: PersonalAccessTokenStatus): 'success' | 'secondary' | 'danger' {
    if (status === 'Active') return 'success';
    if (status === 'Revoked') return 'danger';
    return 'secondary';
  }

  protected load(): void {
    this.loading.set(true);
    this.loadError.set(null);
    this.settingsService.searchMcpTokens()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: response => {
          this.rows.set(response.tokens ?? []);
          this.permissions.set(new PermissionsViewModel(response.permissions));
          this.loading.set(false);
        },
        error: err => {
          this.loading.set(false);
          this.loadError.set(errorText(err, 'The tokens could not be loaded.'));
        },
      });
  }

  protected onGenerate(): void {
    this.draftName.set('');
    this.draftExpiry.set(30);
    this.nameTouched.set(false);
    this.generateError.set(null);
    this.generateOpen.set(true);
  }

  protected onCancelGenerate(): void {
    if (this.generating()) return;
    this.generateOpen.set(false);
  }

  protected onSubmitGenerate(): void {
    this.nameTouched.set(true);
    if (this.nameError() || this.generating()) return;

    this.generating.set(true);
    this.generateError.set(null);
    const name = this.draftName().trim();
    this.settingsService.createMcpToken({ name, expiryDays: this.draftExpiry() })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: created => {
          this.generating.set(false);
          this.generateOpen.set(false);
          this.revealedName.set(created.token.name);
          this.revealedSecret.set(created.secret);
          this.rows.update(rows => [created.token, ...rows]);
        },
        error: err => {
          this.generating.set(false);
          this.generateError.set(errorText(err, 'The token could not be created.'));
        },
      });
  }

  protected onCloseReveal(): void {
    this.revealedSecret.set(null);
    this.revealedName.set('');
  }

  /** User scope, so the server is available in every project (and matches the ~/.claude.json example). */
  private buildClaudeCommand(token: string, withFunctionsKey = this.isHosted): string {
    const parts = [
      `claude mcp add --scope user --transport http ${MCP_SERVER_NAME}`,
      this.mcpUrl,
      `--header "Authorization: Bearer ${token}"`,
    ];
    // The card never knows the real functions system key (§3.13): a placeholder only.
    if (withFunctionsKey) parts.push(`--header "x-functions-key: ${FUNCTIONS_KEY_PLACEHOLDER}"`);
    return parts.join(' ');
  }

  protected async onCopy(text: string, what: string): Promise<void> {
    const ok = await writeToClipboard(text);
    if (ok) this.toast.success(`${what} copied`);
    else this.toast.danger(`${what} could not be copied — select it and copy manually.`);
  }

  protected onRevoke(row: PersonalAccessTokenViewModel): void {
    if (!this.canRevokeRow(row)) return;
    this.pendingRevoke.set(row);
  }

  protected onCancelRevoke(): void {
    if (this.revoking()) return;
    this.pendingRevoke.set(null);
  }

  protected onConfirmRevoke(): void {
    const row = this.pendingRevoke();
    if (!row || this.revoking()) return;
    this.revoking.set(true);
    this.settingsService.revokeMcpToken(new ActionItemCommand(row.instanceId, row.rowVersion))
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: revoked => {
          this.revoking.set(false);
          this.pendingRevoke.set(null);
          this.rows.update(rows => rows.map(r => (r.instanceId === revoked.instanceId ? revoked : r)));
          this.toast.success(`Token "${revoked.name}" revoked`);
        },
        error: err => {
          this.revoking.set(false);
          this.pendingRevoke.set(null);
          this.toast.danger(errorText(err, 'The token could not be revoked.'));
          this.load();
        },
      });
  }
}

function formatTimestamp(value: unknown, empty = ''): string {
  if (!value) return empty;
  const d = new Date(String(value));
  if (Number.isNaN(d.getTime())) return empty;
  return d.toLocaleString(undefined, {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false,
  });
}

function errorText(err: any, fallback: string): string {
  return err?.error?.message ?? (typeof err?.error === 'string' ? err.error : null) ?? fallback;
}
