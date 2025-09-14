type Props = { params: { invoiceId: string } }

export default function ValidatorPage({ params }: Props) {
  return <div>Validation für {params.invoiceId} (Stub)</div>
}

