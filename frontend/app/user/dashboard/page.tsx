"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Cookies from "js-cookie";
import { adsAPI, Ad, PaginatedAdsResponse } from "@/lib/api";

export default function UserDashboard() {
  const [ads, setAds] = useState<Ad[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const router = useRouter();

  const loadAds = useCallback(async () => {
    try {
      setLoading(true);
      const response: PaginatedAdsResponse = await adsAPI.getMyAds(
        currentPage,
        10,
      );
      setAds(response.items);
      setTotalPages(response.pages);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Ошибка загрузки объявлений");
      } else {
        setError("Ошибка загрузки объявлений");
      }
    } finally {
      setLoading(false);
    }
  }, [currentPage]);

  useEffect(() => {
    const token = Cookies.get("access_token");
    if (!token) {
      router.push("/auth/login");
      return;
    }

    loadAds();
  }, [loadAds, router]);

  const handleDelete = async (adId: number) => {
    if (!confirm("Вы уверены, что хотите удалить это объявление?")) return;

    try {
      await adsAPI.deleteAd(adId);
      setAds(ads.filter((ad) => ad.id !== adId));
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Ошибка удаления объявления");
      } else {
        setError("Ошибка удаления объявления");
      }
    }
  };

  const handleLogout = () => {
    Cookies.remove("access_token");
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">Мои объявления</h1>
            <div className="flex space-x-4">
              <button
                onClick={() => router.push("/ads/create")}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Создать объявление
              </button>
              <button
                onClick={handleLogout}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
              >
                Выйти
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {ads.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">У вас пока нет объявлений</p>
            <button
              onClick={() => router.push("/ads/create")}
              className="mt-4 bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700"
            >
              Создать первое объявление
            </button>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {ads.map((ad) => (
              <div
                key={ad.id}
                className="bg-white overflow-hidden shadow rounded-lg"
              >
                {ad.images.length > 0 && (
                  <Image
                    src={ad.images[0].url}
                    alt={ad.title}
                    width={400}
                    height={192}
                    className="w-full h-48 object-cover"
                  />
                )}
                <div className="p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {ad.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {ad.description}
                  </p>
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold text-indigo-600">
                      {ad.price} ₽
                    </span>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => router.push(`/ads/${ad.id}/edit`)}
                        className="text-indigo-600 hover:text-indigo-900 text-sm"
                      >
                        Редактировать
                      </button>
                      <button
                        onClick={() => handleDelete(ad.id)}
                        className="text-red-600 hover:text-red-900 text-sm"
                      >
                        Удалить
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {totalPages > 1 && (
          <div className="mt-8 flex justify-center">
            <nav className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-2 rounded-md text-sm font-medium text-gray-500 bg-white border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
              >
                Предыдущая
              </button>
              <span className="px-3 py-2 text-sm text-gray-700">
                Страница {currentPage} из {totalPages}
              </span>
              <button
                onClick={() =>
                  setCurrentPage(Math.min(totalPages, currentPage + 1))
                }
                disabled={currentPage === totalPages}
                className="px-3 py-2 rounded-md text-sm font-medium text-gray-500 bg-white border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
              >
                Следующая
              </button>
            </nav>
          </div>
        )}
      </main>
    </div>
  );
}
