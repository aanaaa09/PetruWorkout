import sharp from 'sharp';
import { readdir } from 'fs/promises';
import { join } from 'path';

const CONFIGS = [
  // Imágenes de resultados (testimonios)
  {
    inputDir: 'public/images/results',
    sizes: {
      small: 330,
      medium: 660,
      large: 1000
    }
  },
  // Thumbnails de videos
  {
    inputDir: 'public/videos/thumbs',
    sizes: {
      small: 378
    }
  },
  // Imagen hero móvil
  {
    inputDir: 'public/images',
    files: ['petru-hero-nuevo.webp'],
    sizes: {
      optimized: 342
    }
  },
  // Imagen hero desktop
  {
    inputDir: 'public/images',
    files: ['petru-hero.webp'],
    sizes: {
      optimized: 441
    }
  }
];

async function optimizeImages() {
  for (const config of CONFIGS) {
    const { inputDir, sizes, files } = config;

    let fileList;
    if (files) {
      fileList = files;
    } else {
      fileList = await readdir(inputDir);
    }

    for (const file of fileList) {
      if (!file.endsWith('.webp') || file.includes('-small') || file.includes('-medium') || file.includes('-large') || file.includes('-optimized')) {
        continue;
      }

      const inputPath = join(inputDir, file);
      const baseName = file.replace('.webp', '');

      console.log(`\n📸 Procesando: ${file}`);

      for (const [sizeName, width] of Object.entries(sizes)) {
        const outputPath = join(inputDir, `${baseName}-${sizeName}.webp`);

        try {
          await sharp(inputPath)
            .resize(width, null, {
              withoutEnlargement: true,
              fit: 'inside'
            })
            .webp({ quality: 85 })
            .toFile(outputPath);

          console.log(`  ✅ Generado: ${baseName}-${sizeName}.webp (${width}px)`);
        } catch (error) {
          console.error(`  ❌ Error con ${file}:`, error.message);
        }
      }
    }
  }

  console.log('\n ¡Todas las imágenes optimizadas!\n');
  console.log('Archivos generados:');
  console.log('  public/images/results/*-small.webp (330px)');
  console.log('  public/images/results/*-medium.webp (660px)');
  console.log('  public/images/results/*-large.webp (1000px)');
  console.log('  public/videos/thumbs/*-small.webp (378px)');
  console.log('  public/images/petru-hero-nuevo.webp (342px)');
  console.log('  public/images/petru-hero-nuevo.webp (441px)');
}

optimizeImages().catch(console.error);
