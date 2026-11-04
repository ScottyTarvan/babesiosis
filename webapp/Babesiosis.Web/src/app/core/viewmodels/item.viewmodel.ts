export class ItemViewModel<TId> {

  static create<TId>(id: TId, name: string) {
    const vm = new ItemViewModel<TId>();
    vm.id = id;
    vm.name = name;
    
    return vm;
  }

  public id?: TId;
  public name?: string;
  /**
   * The third member of the backend `ListItemViewModel<TId>` — a free-text slot
   * each endpoint uses for whatever the id and name can't carry.
   *
   * `setup-entity-groups-get` fills it two different ways in one response:
   * `linkedServices[].tag` is the linked service's colour, `entityDatasets[].tag` is
   * the owning linked service id as a string (which is how that list gets scoped to a
   * chosen service client-side). Optional, because most endpoints leave it unset.
   */
  public tag?: string;

  constructor(obj?: ItemViewModel<TId> | Partial<ItemViewModel<TId>>) {
    if (obj) {
      this.id = obj.id;
      this.name = obj.name;
      this.tag = obj.tag;
    }
  }

  toString() {
    return this.name;
  }
}
