
import { EditProfileForm } from '@/components/profile/EditProfileForm';
import { NotificationSettings } from '@/components/profile/NotificationSettings';
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
        <NotificationSettings />
      </div>
    </PageWrapper>
  );
}
