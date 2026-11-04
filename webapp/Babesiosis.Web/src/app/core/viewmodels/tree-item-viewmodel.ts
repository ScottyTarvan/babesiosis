export class TreeItemViewModel {
  instanceId?: string;
  id?: string;
  parentId?: string;
  isDirectory?: boolean = false;
  hasItems?: boolean = true;
  name?: string;
  path?: string;
  selected?: boolean = false;
  expanded?: boolean = false;
  children?: TreeItemViewModel[] = [];

  constructor(item?: TreeItemViewModel | Partial<TreeItemViewModel>) {
    if (item) {
      this.instanceId = item.instanceId;
      this.id = item.id;
      this.parentId = item.parentId;
      this.isDirectory = item.isDirectory ?? false;
      this.hasItems = item.hasItems ?? true;
      this.name = item.name;
      this.path = item.path;
      this.selected = item.selected ?? false;
      this.expanded = item.expanded ?? false;
      this.children = item.children?.map(child => new TreeItemViewModel(child)) ?? [];
    }
  }

  toString(): string {
    return `Id: ${this.id}, Name: ${this.name}, Path: ${this.path}, Directory: ${this.isDirectory}`;
  }
}
