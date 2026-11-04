import { ViewModel } from "app/core/viewmodels/viewmodel";
import { parseUtcDate } from "app/core/types/utc-date";

export class AddressViewmodel extends ViewModel {
  line1: string = '';
  line2: string = '';
  suburb: string = '';
  city: string = '';
  province: string = '';
  postalCode: string = '';
  country: string = '';
  createdDate: Date;

  constructor(obj?: Partial<AddressViewmodel>) {
    super(obj as any);
    if (obj) {
      this.line1 = obj.line1 || '';
      this.line2 = obj.line2 || '';
      this.suburb = obj.suburb || '';
      this.city = obj.city || '';
      this.province = obj.province || '';
      this.postalCode = obj.postalCode || '';
      this.country = obj.country || '';
      this.createdDate = parseUtcDate(obj.createdDate) ?? new Date();
    } else {
      this.createdDate = new Date();
    }
  }

  ToString(): string {
    const parts = [
      this.line1,
      this.line2,
      this.suburb,
      this.city,
      this.province,
      this.postalCode,
      this.country,
    ].filter(p => !!p && p.trim().length > 0);

    return parts.join(', ');
  }
}
