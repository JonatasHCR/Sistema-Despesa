
import { EditProfileForm } from '@/components/profile/EditProfileForm';
import PageWrapper from '@/components/layout/PageWrapper';
import Header from '@/components/layout/Header';

export default function ProfilePage() {
  return (
    <PageWrapper>
      <div className="flex flex-col gap-8">
        <Header 
          title="Meu Perfil"
          subtitle="Atualize suas informações pessoais."
        />
        <EditProfileForm />
      </div>
    </PageWrapper>
  );
}
