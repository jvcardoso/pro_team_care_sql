import React from "react";
import SensitiveDataCard from "../ui/SensitiveDataCard";
import AddressRevealCard from "./AddressRevealCard";

interface AddressData {
  id?: string | number;
  street: string;
  number?: string;
  complement?: string;
  details?: string;
  neighborhood: string;
  city: string;
  state: string;
  postal_code?: string;
  zip_code?: string;
  country?: string;
  type: string;
  is_principal?: boolean;
  description?: string;
}

interface AddressDisplayCardProps {
  addresses: AddressData[];
  title?: string;
  getAddressTypeLabel?: (type: string) => string;
  formatZipCode?: (zipCode: string) => string;
  onOpenGoogleMaps?: (address: AddressData) => void;
  onOpenWaze?: (address: AddressData) => void;
  entityType: string;  // e.g., "companies", "clients"
  entityId: number | string;  // ID da entidade pai
}

const AddressDisplayCard: React.FC<AddressDisplayCardProps> = ({
  addresses,
  title = "Endereços",
  getAddressTypeLabel = (type) => type,
  formatZipCode,
  onOpenGoogleMaps,
  onOpenWaze,
  entityType,
  entityId,
}) => {
  const [hasRevealedData, setHasRevealedData] = React.useState(false);

  return (
    <SensitiveDataCard 
      title={title}
      showAutoHideWarning={hasRevealedData}
    >
      {!addresses || addresses.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          Nenhum endereço cadastrado
        </p>
      ) : (
        <div className="space-y-4">
          {addresses.map((address, index) => (
            <AddressRevealCard
              key={address.id || index}
              address={address}
              entityType={entityType as any}
              entityId={Number(entityId)}
              getAddressTypeLabel={getAddressTypeLabel}
              onReveal={() => setHasRevealedData(true)}
              onHide={() => setHasRevealedData(false)}
            />
          ))}
        </div>
      )}
    </SensitiveDataCard>
  );
};

export default AddressDisplayCard;
