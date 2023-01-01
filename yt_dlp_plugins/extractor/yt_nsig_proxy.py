from yt_dlp.utils import ExtractorError, traverse_obj
from yt_dlp.extractor.youtube import YoutubeIE


SOLVER_URL = 'https://yt-dlp-online-utils.vercel.app/youtube/nparams/decrypt'
PREFER_SOLVER = False  # Whether to prefer online solver over local solver


class Youtube_NsigProxyIE(YoutubeIE, plugin_name='NSIG'):
    def __nsig_error(self, current, next, s, video_id, player_url, e):
        self.report_warning(
            f'{current} nsig extraction failed: Trying with {next}\n'
            f'         n = {s} ; player = {player_url}', video_id)
        self.write_debug(e)

    def _decrypt_nsig(self, s, video_id, player_url):
        fallback = True
        try:
            if not player_url or not PREFER_SOLVER:
                return super()._decrypt_nsig(s, video_id, player_url)
        except Exception as e:
            if not player_url:
                raise
            self.__nsig_error('Local', 'online solver', s, video_id, player_url, e)
            fallback = False

        try:
            response_data = self._download_json(
                SOLVER_URL, video_id, query={'player': player_url, 'n': s},
                note='Requesting nsig decryption from online solver')
            if response_data['status'] != 'ok':
                raise ExtractorError(f'Failed at step "{response_data["step"]}":\n    '
                                     f'{traverse_obj(response_data, ("data", "message"))}')
            self.write_debug(f'Decrypted nsig {s} => {response_data["data"]}')
            return response_data['data']
        except Exception as e:
            if not fallback:
                raise
            self.__nsig_error('Online', 'local solver', s, video_id, player_url, e)
            return super()._decrypt_nsig(s, video_id, player_url)


__all__ = []
